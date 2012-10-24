# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# TODO
# CaptchableView in generiv_utils, figure out to use captcha
# prestabilire gli urls standard
#################################### new stuff
import os, re, time
from datetime import datetime, timedelta, date

from django.conf import settings
from django.http import HttpResponseRedirect, urlparse
from django.core.urlresolvers import reverse
from django.forms import fields as forms_fields, widgets as forms_widgets
from django.views.generic import TemplateView, FormView, DetailView
from django.views.generic.edit import CreateView, BaseUpdateView, UpdateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import classonlymethod, method_decorator
from django.utils.translation import ugettext as _
from django.utils.log import getLogger

from django.contrib.auth import (authenticate, login as auth_login,
                                 logout as auth_logout, REDIRECT_FIELD_NAME)
from django.contrib.auth.models import User
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm, UserChangeForm,
                                       PasswordChangeForm, PasswordResetForm, SetPasswordForm)
#from django.contrib.auth.decorators import login_required
                                       
from django.contrib.aderit.access_account.models import AccessAccount
from django.contrib.aderit.generic_utils.views import GenericUtilView

from account.models import Account

## maybe in CaptchableView
HAS_CAPTCHA = 'captcha' in settings.INSTALLED_APPS
USE_CAPTCHA_SIGNUP = HAS_CAPTCHA and getattr(settings,'CAPTCHA_SIGNUP',True)
USE_CAPTCHA_CHPSW = HAS_CAPTCHA and getattr(settings,'CAPTCHA_CHPSW',False)
USE_CAPTCHA_CHPROFILE = HAS_CAPTCHA and getattr(settings,'CAPTCHA_CHPROFILE',False)
USE_CAPTCHA_FORGOTPSW = HAS_CAPTCHA and getattr(settings,'CAPTCHA_FORGOTPSW',True)
USE_CAPTCHA_RESETPSW = HAS_CAPTCHA and getattr(settings,'CAPTCHA_RESETPSW',False)

logger = getLogger('django.debug')

# CaptchableView should be a (FormView, GenericUtilView) and decorate dispatch
class CaptchableView(GenericUtilView):
    use_captcha = False
    captcha_field_name = 'captcha'

    def maybe_add_captcha(self, form_k):
        if HAS_CAPTCHA and self.use_captcha:
            from captcha.fields import CaptchaField
            captcha_field = CaptchaField(label=_("*Inserire Captcha"),
                                         help_text = _("(obbligatorio la per sicurezza)"))
            form_k.base_fields.update({ self.captcha_field_name : captcha_field })

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        logger.debug("Captcha dispatch")
        self.setup_attrs(**kwargs)
        return super(CaptchableView, self).dispatch(request, *args, **kwargs)

class AccountLoginView(CaptchableView):
    """
    Class based view, copied from django.contrib.auth.views.login

    Displays the login form and handles the login action.
    """
    template_name='registration/login_as_ul.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    ## TODO: figure out to use success_url
    redirect_to = getattr(settings, 'LOGIN_REDIRECT_URL', "")
    form_class = None
    current_app = None
    use_captcha = False
    captcha_form_class = None

    def get_initial(self):
        initial = super(AccountLoginView, self).get_initial()
        initial.update({ self.redirect_field_name : self.redirect_to })
        return initial

    def get_form_class(self):
        if self.form_class is not None:
            return super(AccountLoginView, self).get_form_class()

        self.form_class = AuthenticationForm

        form_k = super(AccountLoginView, self).get_form_class()

        self.redirect_to = self.request.REQUEST.get(self.redirect_field_name, self.redirect_to)

        netloc = urlparse.urlparse(self.redirect_to)[1]
        if netloc and netloc != self.request.get_host():
            self.redirect_to = getattr(settings, 'LOGIN_REDIRECT_URL', "")

        # add input hidden for redirection
        hidden_widget=forms_widgets.HiddenInput(attrs={'value': self.redirect_to})
        next_field = forms_fields.CharField(widget=forms_widgets.HiddenInput)
        form_k.base_fields.update({self.redirect_field_name: next_field})

        self.maybe_add_captcha(form_k)

        self.form_class = form_k ## put in self for get_initial check later
        return self.form_class


    ## POST related mathod
    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        
        return HttpResponseRedirect(self.redirect_to)

    def form_invalid(self, form):
        self.request.session.set_test_cookie()
        current_site = get_current_site(self.request)
        
        context = self.get_context_data(**{'form': form,
                                           self.redirect_field_name: self.redirect_to,
                                           'site': current_site,
                                           'site_name': current_site.name})
        return TemplateResponse(self.request, self.template_name, context,
                                current_app=self.current_app)

class AccountLogoutView(TemplateView):
    """
    Class based view, copied from django.contrib.auth.views.logout

    Logs out the user and displays 'You are logged out' message.
    """
    template_name='registration/logged_out.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_to = None
    current_app = None
    next_page = None

    def get(self, request, *args, **kwargs):
        auth_logout(self.request)
        self.redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')
        if self.redirect_to:
            netloc = urlparse.urlparse(self.redirect_to)[1]
            # Security check -- don't allow redirection to a different host.
            if not (netloc and netloc != self.request.get_host()):
                return HttpResponseRedirect(self.redirect_to)

        if self.next_page is None:
            current_site = get_current_site(self.request)
            context = self.get_context_data(site=current_site,
                                            site_name=current_site.name,
                                            title=_('Logged out'))
            return TemplateResponse(self.request, self.template_name, context,
                                    current_app=self.current_app)
        else:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(self.next_page or self.request.path)


class AccountUpdateView(UpdateView, CaptchableView):
    model = None
    success_url = ""
    template_name = ""
    form_class = None
    use_captcha = True
    captcha_form_class = None
    
    def get_form_class(self):
        if self.form_class is not None:
            return super(AccountUpdateView, self).get_form_class()
        
        form_k = super(AccountUpdateView, self).get_form_class()
        form_k.base_fields['user'] = forms_fields.CharField()
        # if self.use_captcha and self.captcha_form_class is not None:
        #     #form_k = type('ChProfileForm1', (form_k.__bases__[0], self.captcha_form_class,), {})
        #     #form_k.base_fields.update(self.captcha_form_class.base_fields)
        #     self.add_captcha(form_k)
        self.maybe_add_captcha(form_k)
        self.form_class = form_k
        return self.form_class

    def get_object(self, queryset=None):
        slug = (isinstance(self.kwargs.get('slug', None), basestring) and \
                    self.kwargs.get('slug').isdigit() and \
                    int(self.kwargs.get('slug'))) or \
                    (isinstance(self.kwargs.get('slug', None), int) and self.kwargs.get('slug'))
        if self.request.user.is_superuser or slug == self.request.user.account.id:
            return Account.objects.get(id=slug)
        return self.request.user.account

class AccountSignupView(CreateView):
    model = None
    success_url = ""
    template_name = "registration/signup_as_ul.html"
    form_class = None
    use_captcha = False
    captcha_form_class = None

    def get_form_class(self):
        if self.form_class is not None:
            return super(AccountSignupView, self).get_form_class()
        
        form_k = super(AccountSignupView, self).get_form_class()
        form_k = type('ChProfileForm1', (form_k, self.captcha_form_class,), {})
        #form_k.base_fields['user'] = forms_fields.CharField()
        del form_k.base_fields['user']
        # if self.use_captcha and self.captcha_form_class is not None:
        #     #form_k = type('ChProfileForm1', (form_k, self.captcha_form_class,), {})
        #     self.add_captcha(form_k)            
        self.maybe_add_captcha(form_k)
        self.form_class = form_k
        return self.form_class
    


### old stuff
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.forms import fields as forms_fields, widgets as forms_widgets
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView, ProcessFormView, CreateView, UpdateView
from django.contrib.sites.models import Site, get_current_site
from django.contrib.auth import (authenticate, login as auth_login,
                                 logout as auth_logout, REDIRECT_FIELD_NAME)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import classonlymethod, method_decorator
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect

from django.contrib.aderit.access_account.models import AccessAccount
from django.contrib.aderit.generic_utils.views import GenericUtilView
from django.contrib.aderit.generic_utils.currentUserMiddleware import get_current_user
from django.contrib.aderit.generic_utils.templatetags.nice_name import nice_name

from account.models import *
from account.forms import *

import logging, os, re, time, urlparse
from datetime import datetime, timedelta, date

logger = logging.getLogger('django.debug')
logger.addHandler(logging.StreamHandler())
logger.handlers[0].setFormatter(logging.Formatter("%(name)s:%(levelname)s: %(message)s"))
logger.setLevel(logging.DEBUG)

CAPTCHA_SIGNUP = getattr(settings,'CAPTCHA_SIGNUP',True)
CAPTCHA_CHPSW = getattr(settings,'CAPTCHA_CHPSW',False)
CAPTCHA_CHPROFILE = getattr(settings,'CAPTCHA_CHPROFILE',False)
CAPTCHA_FORGOTPSW = getattr(settings,'CAPTCHA_FORGOTPSW',True)
CAPTCHA_RESETPSW = getattr(settings,'CAPTCHA_RESETPSW',False)
if 'captcha' not in settings.INSTALLED_APPS:
    CAPTCHA_SIGNUP = False
    CAPTCHA_CHPSW = False
    CAPTCHA_CHPROFILE = False
    CAPTCHA_FORGOTPSW = False
    CAPTCHA_RESETPSW = False

#TODO Pulire i vari import e le varie variabili


class AccountUpdateCurrentView(UpdateView, GenericUtilView):
    model = None
    success_url = ""
    template_name = ""
    use_captcha = CAPTCHA_CHPROFILE
    form_class = None
    
    def get_form_class(self):
        if self.form_class is not None:
            return super(self.__class__, self).get_form_class()
        
        ## TODO: add some fields from auth.User
        form_k = super(self.__class__, self).get_form_class()
        #logger.debug("user attrs: %s", form_k.base_fields)
        del form_k.base_fields['user']
        
        if self.request.user.is_authenticated() and self.use_captcha:
            form_k = type('ChProfileForm1', (form_k, CaptchaForm,), {})
        return form_k

    def get_object(self, queryset=None):
        return self.request.user.account

class AccountLogoutView(TemplateView, GenericUtilView):
    """
    Class based view, copied from django.contrib.auth.views.logout

    Logs out the user and displays 'You are logged out' message.
    """
    template_name='registration/logged_out.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_to = None
    current_app = None
    next_page = None

    def get(self, request, *args, **kwargs):
        auth_logout(self.request)
        self.redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')
        if self.redirect_to:
            netloc = urlparse.urlparse(self.redirect_to)[1]
            # Security check -- don't allow redirection to a different host.
            if not (netloc and netloc != self.request.get_host()):
                return HttpResponseRedirect(self.redirect_to)

        if self.next_page is None:
            current_site = get_current_site(self.request)
            context = self.get_context_data(site=current_site,
                                            site_name=current_site.name,
                                            title=_('Logged out'))
            return TemplateResponse(self.request, self.template_name, context,
                                    current_app=self.current_app)
        else:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(self.next_page or self.request.path)

class AccountResetPasswordView():
    """
    View to reset password for current user.
    """
    model = None
    success_url = ""
    template_name = ""
    use_captcha = CAPTCHA_CHPROFILE


### old stuff
class AccessAccountView(FormView):

    form_class = None
    ok = None
    signup = False
    chpsw = False
    chprofile = False
    forgotpsw = False
    resetpsw = False
    iduser = ""
    success_url = ""

    def get_form_class(self):
        if not self.form_class is None:
            val = super(AccessAccountView, self).get_form_class()
            return val
        
        name = None
        attrs = {}

        #SIGNUP FORM
        if not self.request.user.is_authenticated() and self.signup:
	    if 'captcha' in settings.INSTALLED_APPS and CAPTCHA_SIGNUP: form_k = type(name or 'SignupForm1', (AccessAccountSignupForm,CaptchaForm,), attrs)
	    else: form_k = type(name or 'SignupForm1', (AccessAccountSignupForm,), attrs)
            return form_k

        #CHPSW FORM
        if self.request.user.is_authenticated() and self.chpsw:
            if 'captcha' in settings.INSTALLED_APPS and CAPTCHA_CHPSW: form_k = type(name or 'ChPswForm1', (ChPsw,CaptchaForm), attrs)
	    else: form_k = type(name or 'ChPswForm1', (ChPsw,), attrs)
            return form_k

        #CHPROFILE FORM
        if self.request.user.is_authenticated() and self.chprofile:
            if 'captcha' in settings.INSTALLED_APPS and CAPTCHA_CHPROFILE: form_k = type(name or 'ChProfileForm1', (AccessAccountProfileForm,CaptchaForm,), attrs)
            else: form_k = type(name or 'ChProfileForm1', (AccessAccountProfileForm,), attrs)
            return form_k

        #FORGOTPSW FORM
        if not self.request.user.is_authenticated() and self.forgotpsw:
            if 'captcha' in settings.INSTALLED_APPS and CAPTCHA_FORGOTPSW: form_k = type(name or 'ForgotPswForm1', (ForgotPswUsernameForm,CaptchaForm,), attrs)
	    else: form_k = type(name or 'ForgotPswForm1', (ForgotPswUsernameForm,), attrs)
            return form_k
           
        #RESETPSW FORM
        if not self.request.user.is_authenticated() and self.resetpsw:
            if 'captcha' in settings.INSTALLED_APPS and CAPTCHA_RESETPSW: form_k = type(name or 'ResetPswForm1', (ResetPswForm,CaptchaForm,), attrs)
	    else: form_k = type(name or 'ResetPswForm1', (ResetPswForm,), attrs)
            return form_k

        #LOGIN FORM (???)       
        if self.request.user.is_authenticated(): return AuthenticationForm

        #LOGIN FORM
        return AuthenticationForm
    
    def get_context_data(self, **kwargs):
        from django.template import RequestContext
        kwargs.update({
                'signup':self.signup,
                'chpsw':self.chpsw, 
                'chprofile':self.chprofile, 
                'forgotpsw':self.forgotpsw,
                'resetpsw':self.resetpsw
                }) 
        super_context = super(AccessAccountView, self).get_context_data(**kwargs)
        context = RequestContext(self.request, super_context)
        return context

    def get_success_url(self):
        #TODO Controllare e rendere configurabile
        try:
            val = None
            val = super(AccessAccountView, self).get_success_url()
        except:
            val = HttpResponseRedirect(".")
        if self.signup: return reverse('profile')
        if self.chpsw: return reverse('profile')
        if self.chprofile: return reverse('profile')
        if self.forgotpsw: return reverse('forgotpsw')
        if self.resetpsw: return reverse('resetpsw')
        return val

    def form_valid(self, form):
        #TODO Sostituire tutta la post qui all'interno per pulizia
        #TODO Rendere configurabile la possibilita' di ogni cosa da settings getattr(...)
        val = super(AccessAccountView, self).form_valid(form)
        self.form_is_valid = True
        return val

    def get_initial(self):
        initial = {}
        if self.chprofile:
            accessuser = Account.objects.get(user=self.request.user)
            initial.update({'nickname': self.request.user.username})
            initial.update({'first_name': self.request.user.first_name})
            initial.update({'last_name': self.request.user.last_name})
            initial.update({'email': self.request.user.email})
            initial.update({'phone': accessuser.phone})
            initial.update({'mobile_phone': accessuser.mobile_phone})
            initial.update({'company': accessuser.company})
            initial.update({'address': accessuser.address})
            initial.update({'cap': accessuser.cap})
            initial.update({'location': accessuser.location})
            initial.update({'paese': accessuser.paese})
        return initial

    def get(self, request, *args, **kwargs):
        #TODO Pulire
        #logger.debug("get (%s, %s) -> %s -- self_U: %s -- req_U: %s", args, kwargs, self.request.path, self.request.user, request.user)
        if kwargs.has_key('action'):
            #log.error("ACTION KEY IN GET = %s", kwargs.get('action'))
            if kwargs.get('action') == 'signup': self.signup = True
            if kwargs.get('action') == 'chpsw': self.chpsw = True
            if kwargs.get('action') == 'chprofile': self.chprofile = True
            if kwargs.get('action') == 'forgotpsw': self.forgotpsw = True
            if kwargs.get('action') == 'resetpsw': 
		self.resetpsw = True
                try:
                    self.iduser = request.GET['id']
                    #log.error("IN GET IDUSER = %s", self.iduser)
                except:
                    pass
            if kwargs.get('action') == 'logout':
                logout(request)
                return HttpResponseRedirect("/")             
        val = super(AccessAccountView, self).get(request, *args, **kwargs)
        #logger.debug("get return: %s", val)
        ##logger.debug("get REQ: %s", self.request)
        return val

    def post(self, request, *args, **kwargs):
        #TODO Pulire e minimizzare con la form valid
        if kwargs.has_key('action'):
            #log.error("ACTION KEY IN POST = %s", kwargs.get('action'))
            if kwargs.get('action') == 'signup': self.signup = True
            if kwargs.get('action') == 'chpsw': self.chpsw = True
            if kwargs.get('action') == 'chprofile': self.chprofile = True
            if kwargs.get('action') == 'forgotpsw': self.forgotpsw = True
            if kwargs.get('action') == 'resetpsw': self.resetpsw = True
        #logger.debug("post [req: %s] (%s, %s) -- SELF path: %s", request, args, kwargs, self.request.path)
        val = super(AccessAccountView, self).post(request, *args, **kwargs)
        #logger.debug("post form is valid: %s", getattr(self, 'form_is_valid', False))
        if getattr(self, 'form_is_valid', False):
            if self.resetpsw:
                #logger.error("IN RESETPSW")
                #logger.error("ID %s", self.iduser)
                try:
                    self.iduser = request.GET['id']
                    reset_psw = ResettablePassword.objects.get(session=self.iduser)
                    date_limit = datetime.now() - timedelta(days=2)
                    if reset_psw.date < date_limit:
                        #logger.error("troppo vecchia, da eliminare")
                        reset_psw.delete()
                        return HttpResponseRedirect(".?id=%s&error=True" % self.iduser)
                    user = reset_psw.user
                    new_psw = self.request.POST['password_new']
                    conf_new_psw = self.request.POST['password_new_confirm']
                    user.set_password(new_psw)
                    user.save() 
                    reset_psw.delete()
                    var = 'chpsw'
                    #self._notify_user_via_mail(access_user, var)
                    return val
		except Exception, e:
                    #logger.error("Exc in RESETPSW %s", e)
                    return HttpResponseRedirect(".?id=%s&error=True" % self.iduser)
            if self.forgotpsw:
                #logger.error("IN FORGOTPSW %s", self.request.POST['username'])
                try:
                    #logger.error("usermail %s", self.request.POST['username'])
                    user = User.objects.get(username=self.request.POST['username'])
                    self._notify_user_via_mail_forgotpsw(user, request.session)
                except Exception, e:
                    logger.error("Exc in forgotpsw for name %s, %s", self.request.POST['username'], e)
                    pass
                return val
            if self.chprofile:
                user = request.user
                #logger.error("IN CHPROFILE %s", user)
                try:
                    access_user = Account.objects.filter(user=user)[0]
                except:
                    raise forms.ValidationError(("User Access Not Found"))
                try:
                    access_user.phone = self.request.POST['phone']
                    access_user.mobile_phone = self.request.POST['phone_mobile']
                    access_user.cap = self.request.POST['cap']
                    access_user.location = self.request.POST['location']
                    access_user.paese = self.request.POST['paese']
                    access_user.company = self.request.POST['company']
                    access_user.address= self.request.POST['address']
                    access_user.partita_iva = self.request.POST['partita_iva']
                    access_user.save()
                    user.first_name = self.request.POST['first_name']
                    user.last_name = self.request.POST['last_name']
                    user.email = self.request.POST['email']
                    user.username = self.request.POST['nickname']
                    user.save()
                    var = 'chprofile'
                    #self._notify_user_via_mail(access_user, var)
                    return val
                except Exception, e:
                    logger.debug('Exception occurred during changing profile: %s', e)
                    return val
            if self.chpsw:
                user = request.user
                #logger.debug("IN CHPSW %s", user)
                try:
                    old_psw = self.request.POST['password_old']
                    if user.check_password(old_psw):
                        new_psw = self.request.POST['password_new']
                        conf_new_psw = self.request.POST['password_new_confirm']
                        user.set_password(new_psw)
                        user.save()
                        var = 'chpsw'
                        #self._notify_user_via_mail(access_user, var)
                        return val
                    else:
                        raise forms.ValidationError(("Reinserire la vecchia password"))
                except Exception, e:
                    logger.debug('Exception occurred during changing psw: %s', e)
                    return val
            if self.signup:
                try:
                    usernew = Account()
                    user = User()
                    #logger.debug("USER-CREATING - %s", self.request.POST['email'])
                    user.email = self.request.POST['email']
                    user.username = self.request.POST['nickname']
                    user.first_name = self.request.POST['first_name']
                    user.last_name = self.request.POST['last_name']
		    user.is_active = True
                    usernew.phone = self.request.POST['phone']
                    usernew.mobile_phone = self.request.POST['phone_mobile']
                    usernew.company = self.request.POST['company']
                    usernew.address = self.request.POST['address']
                    usernew.cap = self.request.POST['cap']
                    usernew.location = self.request.POST['location']
                    usernew.paese = self.request.POST['paese']
                    user.set_password(self.request.POST['password'])
		    user.save()
                    usernew.user = user
		    usernew.save()
                    #logger.debug("USER-CREATED - %s", self.request.POST['nickname'])
                    user = authenticate(username=self.request.POST['nickname'],
                                    password=self.request.POST['password'])
	            login(self.request, user)
                except Exception, e:
                    logger.debug("Exception occurred during creation of USER %s -- %s", self.request.POST['nickname'], e)
                    return val 
                var = 'signup'
                #self._notify_user_via_mail(usernew, var)
                #self._notify_admin_via_mail_for_new_user(usernew, var)
                return val
            try:
                user = authenticate(username=self.request.POST['username'],
                                    password=self.request.POST['password'])
                #logger.debug("authenticate return: %s", user)
                if user is not None:
                    if user.is_active:
                        #logger.debug("You provided a correct username and password!")
                        login(self.request, user)
                        #logger.debug("Login ret: %s", self.request.user)
                        var = 'login'
                        #self._notify_user_via_mail(self.request.user, var)
                        try:
                            Account.objects.get(user=user)
                            logger.error("%s Existing AccessAccount",user)
                        except Exception, e:
                            #logger.error("Not existing %s AccessAccount: %s", user, e)
                            try:
                                new = Account()
                                new.user = user
                                new.save()
                            except Exception, e:
                                logger.error("Problems in creating %s Account from auth in auto: %s", user, e)
                        if not request.user.email:
			    #logger.error("Utente creato in auto, non ha l'email: ragionare a fondo su come mandarlo per forza a modificare le sue credenziali la prima volta")
                            return HttpResponseRedirect('/access/chprofile/?newuser=True')
                        else:
                            redirect_to = request.REQUEST.get('next', '')
                            if not redirect_to:
                                redirect_to = "/"
                            #logger.error("REDIREZIONE A: %s", redirect_to)
                            return HttpResponseRedirect(redirect_to)
                    else:
                        logger.debug("Your account has been disabled!")
                else:
                    logger.debug("Your username and password were incorrect.")
            except Exception, e:
                logger.error("Auth Error: %s", e)
        else: # INVALID, to still here
            return super(AccessAccountView, self).get(request, *args, **kwargs)
        return HttpResponseRedirect('/') #val


    def _notify_user_via_mail_forgotpsw(self, user, session):
        try:
            mailto = user.email
            if len(ResettablePassword.objects.filter(user=user)) > 0:
                resettable_psw = ResettablePassword.objects.get(user=user)
                resettable_psw.session = session.session_key + user.username
                resettable_psw.save()
            else:
                resettable_psw = ResettablePassword()
                resettable_psw.user = user
                resettable_psw.session = session.session_key + user.username
                resettable_psw.date = datetime.now()
                resettable_psw.save()
        except Exception, e:
            logger.error("Exc in send mail, no email?? %s", e)
            mailto = None
	kwargs = {'type':'forgotpsw','mailto':[mailto], 'type_dict':'single', mailto : {'user': nice_name(user), 'link' : Site.objects.get_current().domain +"/access/resetpsw/?id="+ session.session_key + user.username }}
        return SendTypeMail(kwargs)

