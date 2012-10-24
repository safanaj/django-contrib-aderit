# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# TODO
# * prestabilire gli urls standard
# * minimizzare i templates necessarie usando
#   get_template_names() e schemi del tipo:
#   "%s_%s.html" % ('account', 'form_as_ul') ... 
# * pulire imports
#################################### new stuff
from django.conf import settings
from django.http import HttpResponseRedirect, urlparse
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.forms import fields as forms_fields, widgets as forms_widgets, models as forms_models
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.utils.translation import ugettext as _
from django.utils.log import getLogger

from django.contrib.sites.models import get_current_site
from django.contrib.auth import (authenticate, login as auth_login,
                                 logout as auth_logout, REDIRECT_FIELD_NAME)
from django.contrib.auth.models import User, SiteProfileNotAvailable
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm, UserChangeForm,
                                       AdminPasswordChangeForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm)
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.tokens import default_token_generator

from django.contrib.aderit.generic_utils.views import GenericUtilView, GenericProtectedView, GenericProtectedUncacheableView
from django.contrib.aderit.generic_utils.forms import generic_formclass_factory, SortedDict
from django.contrib.aderit.send_mail.views import SendTypeMail ## to move in utils.py
from django.contrib.aderit.access_account import _get_model_from_auth_profile_module

## maybe in CaptchableView
HAS_CAPTCHA = 'captcha' in settings.INSTALLED_APPS
USE_CAPTCHA_SIGNUP = HAS_CAPTCHA and getattr(settings,'CAPTCHA_SIGNUP',True)
USE_CAPTCHA_CHPSW = HAS_CAPTCHA and getattr(settings,'CAPTCHA_CHPSW',False)
USE_CAPTCHA_CHPROFILE = HAS_CAPTCHA and getattr(settings,'CAPTCHA_CHPROFILE',False)
USE_CAPTCHA_FORGOTPSW = HAS_CAPTCHA and getattr(settings,'CAPTCHA_FORGOTPSW',True)
USE_CAPTCHA_RESETPSW = HAS_CAPTCHA and getattr(settings,'CAPTCHA_RESETPSW',False)
if HAS_CAPTCHA:
    from captcha.fields import CaptchaField
CAPTCHA_FIELD_CLASS = (HAS_CAPTCHA and CaptchaField) or None

logger = getLogger('aderit.access_account.views')

def _maybe_add_captcha(self, actual_fields):
    if self.use_captcha and HAS_CAPTCHA and self.captcha_field_class is not None:
        if self.captcha_field is None:
            self.captcha_field = self.captcha_field_class(label=_("Inserire Captcha"),
                                                          help_text = _("(obbligatorio la per sicurezza)"))
        actual_fields.update({ self.captcha_field_name : self.captcha_field })

class CaptchableView(GenericProtectedView):
    use_captcha = False
    captcha_field_class = CAPTCHA_FIELD_CLASS
    captcha_field_name = 'captcha'
    captcha_field = None

class LoginView(FormView, CaptchableView):
    """
    Class based view, copied from django.contrib.auth.views.login

    Displays the login form and handles the login action.
    """
    model = _get_model_from_auth_profile_module()
    template_name='registration/login_as_ul.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    ## TODO: figure out how to use success_url
    redirect_to = getattr(settings, 'LOGIN_REDIRECT_URL', "")
    current_app = None
    authentication_form_class = AuthenticationForm

    def get_initial(self):
        initial = super(LoginView, self).get_initial()
        initial.update({ self.redirect_field_name : self.redirect_to })
        return initial

    def get_form_class(self):
        if self.form_class is not None:
            return super(LoginView, self).get_form_class()

        self.redirect_to = self.request.REQUEST.get(self.redirect_field_name, self.redirect_to)

        netloc = urlparse(self.redirect_to)[1]
        if netloc and netloc != self.request.get_host():
            self.redirect_to = getattr(settings, 'LOGIN_REDIRECT_URL', "")

        additional_fields = SortedDict()
        # add input hidden for redirection
        hidden_widget=forms_widgets.HiddenInput(attrs={'value': self.redirect_to})
        next_field = forms_fields.CharField(widget=forms_widgets.HiddenInput)
        additional_fields.update({ self.redirect_field_name: next_field })

        _maybe_add_captcha(self, additional_fields)

        return generic_formclass_factory([],
                                         bases=[self.authentication_form_class],
                                         sorted_fields=additional_fields)

    ## POST related mathod
    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()

        if self.current_app is None:
            self.current_app = self.model.__name__.lower()

        if self.request.user == form.get_user():
            try:
                self.request.user.get_profile()
            except (self.model.DoesNotExist, AttributeError):
                self.model(user=self.request.user).save()
        
        return HttpResponseRedirect(self.redirect_to)

    def form_invalid(self, form):
        self.request.session.set_test_cookie()
        current_site = get_current_site(self.request)
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()

        if self.current_app is None:
            self.current_app = self.model.__name__.lower()
        
        context = self.get_context_data(**{'form': form,
                                           self.redirect_field_name: self.redirect_to,
                                           'site': current_site,
                                           'site_name': current_site.name})
        return TemplateResponse(self.request, self.template_name, context,
                                current_app=self.current_app)

class UpdateView(UpdateView, CaptchableView):
    model = _get_model_from_auth_profile_module()
    slug = None
    exclude_formfields = ['user', 'password', 'user_permissions',
                          'is_staff', 'is_superuser', 'is_active',
                          'groups', 'last_login', 'date_joined']
    user_change_form_class = UserChangeForm

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return ""

    def get_form_class(self):
        if self.form_class is not None:
            return super(UpdateView, self).get_form_class()

        super_form_k = super(UpdateView, self).get_form_class()
        super_form_k.base_fields = {}
        form_k = generic_formclass_factory([], sorted_fields=self.user_change_form_class.base_fields,
                                           prepend_fields=True,
                                           bases=[super_form_k])
        for k in self.exclude_formfields:
            if form_k.base_fields.has_key(k):
                del form_k.base_fields[k]

        _maybe_add_captcha(self, form_k.base_fields)

        return form_k

    def get_initial(self):
        if self.object is None: return {}
        initial = {}
        rel_fields = []
        for f in self.object._meta.fields:
            if f.rel:
                rel_fields.insert(0, f)
                continue
            initial.update({ f.name : getattr(self.object, f.name) })
        ## Too much invasive, should respect concrete model properties.
        ## Also have to prefix according with get_form_class / generic_formclass_factory
        for rel_f in rel_fields:
            related_obj = getattr(self.object, rel_f.name)
            for f in related_obj._meta.fields:
                if initial.has_key(f.name):
                    initial.update({ rel_f.name + "_" + f.name : getattr(related_obj, f.name) })
                else:
                    initial.update({ f.name : getattr(related_obj, f.name) })
        return initial

    def get_object(self, queryset=None):
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        try:
            account = self.model.objects.get(**{ self.slug_field : self.slug })
        except (self.model.DoesNotExist, AttributeError):
            account = None
        ### TODO: rewite in a simpler way
        try:
            current_account = self.request.user.get_profile()
        except (self.model.DoesNotExist, AttributeError):
             current_account = None
        if (self.request.user.is_superuser and self.slug) or \
          (not (current_account is None) and (account == current_account)):
            return account
        try:
            return self.request.user.get_profile()
        except (self.model.DoesNotExist, AttributeError):
            return None
    
    ## POST related method
    def form_valid(self, form):
        ### TODO: put interesting fields in an instance variable list
        if self.object is None: return redirect_to_login(self.request.path)
        if form.has_changed():
            for k, v in form.data.items():
                if not k in form.changed_data:
                    continue
                if k in [f.name for f in self.model._meta.fields if not f.name in ['id', 'pk', 'user', 'user_id']]:
                    setattr(self.object, k, v)
                elif k in [f.name for f in self.object.user._meta.fields if not f.name in ['id', 'pk']]:
                    setattr(self.object.user, k, v)
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class SignupView(CreateView, GenericProtectedUncacheableView, CaptchableView):
    model = _get_model_from_auth_profile_module()
    template_name = "registration/signup_as_ul.html"
    user_create_form_class = UserCreationForm
    exclude_formfields = ['user']
    slug = None
    success_url = "/"
    
    def get_initial(self):
        return {}
    
    def get_form_class(self):
        if self.form_class is not None:
            return super(SignupView, self).get_form_class()

        super_form_k = super(SignupView, self).get_form_class()
        # form_k = generic_formclass_factory([], prepend_fields=True,
        #                                    sorted_fields=self.user_create_form_class.base_fields,
        #                                    bases=[super_form_k])
        form_k = generic_formclass_factory([super_form_k],
                                           bases=[self.user_create_form_class])
        for k in self.exclude_formfields:
            if form_k.base_fields.has_key(k):
                del form_k.base_fields[k]

        _maybe_add_captcha(self, form_k.base_fields)

        return form_k

    def form_valid(self, form):
        new_user = User.objects.create_user(username=form.data['username'],
                                            password=form.data['password1'],
                                            email=form.data.get('email', None))
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        account_kwargs = {}
        for fname in [f.name for f in self.model._meta.fields if not f.name in ['pk', 'id', 'user']]:
            if form.data.has_key(fname):
                account_kwargs.update({ fname : form.data[fname] })
        try:
            self.object = new_user.get_profile()
        except (self.model.DoesNotExist, AttributeError):
            self.object = self.model(user=new_user, **account_kwargs)
            self.object.save()
        else:
            rows = self.model.objects.filter(pk=self.object.pk).update(**account_kwargs)
            assert(rows == 1 or rows == len(account_kwargs) == 0)
        return HttpResponseRedirect(self.get_success_url())

class ChangePasswordView(FormView, GenericProtectedUncacheableView, CaptchableView):
    model = _get_model_from_auth_profile_module()
    slug = None
    slug_field = 'id'
    password_change_form_class = PasswordChangeForm
    admin_password_change_form_class = AdminPasswordChangeForm
    change_done_template_name = 'account/chpsw.html'

    def get_initial(self):
        # initially always empty form
        return {}

    def get_form_class(self):
        if self.request.user.is_superuser:
            return self.admin_password_change_form_class
        return self.password_change_form_class

    def get_form(self, form_class):
        logger.debug("Form for current user: %s", form_class(self.request.user).as_p())
        if self.slug is None:
            return form_class(self.request.user, **self.get_form_kwargs())
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        try:
            account = self.model.objects.get(**{ self.slug_field : self.slug })
            if not (self.request.user.is_superuser or self.request.user == account.user):
                account = self.request.user.get_profile()
        except (self.model.DoesNotExist, AttributeError):
            return form_class(self.request.user, **self.get_form_kwargs())
        return form_class(account.user, **self.get_form_kwargs())

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect_to_login(self.request.path)
        return super(ChangePasswordView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return TemplateResponse(self.request, self.change_done_template_name)

################## Without Form Views
class LogoutView(TemplateView):
    """
    Class based view, copied from django.contrib.auth.views.logout

    Log out the user and displays 'You are logged out' message.
    """
    template_name='registration/logged_out.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_to = None
    current_app = None
    next_page = None

    def get(self, request, *args, **kwargs):
        auth_logout(self.request)
        self.redirect_to = self.request.REQUEST.get(self.redirect_field_name,
                                                    self.redirect_to or '')
        if self.redirect_to:
            netloc = urlparse(self.redirect_to)[1]
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

class DetailView(DetailView, GenericUtilView):
    slug_field = 'pk'

    def get_object(self):
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        if self.kwargs.get('slug', None) is None and self.request.user.is_authenticated():
            try:
                return self.request.user.get_profile()
            except (self.model.DoesNotExist, AttributeError):
                return None
        try:
            return self.model.objects.get(**{ self.slug_field : self.kwargs.get('slug', None) })
        except:
            return None

class ForgotPasswordView(FormView, CaptchableView):
    success_template_name = 'account/forgot_psw_ok.html'
    send_mail_type_name = 'forgot password'
    delete_token_after_use = True
    token = None
    slug_field = 'token'
    success_url = '/'
    protocol_for_link = 'http'

    def get_form_class(self):
        if self.token is not None:
            ## here, from link in email sent yet
            return generic_formclass_factory(AdminPasswordChangeForm)
        ## token is None, ask for email to send
        return generic_formclass_factory(PasswordResetForm)

    def form_valid(self, form):
        if self.token is not None:
            ### form is valid, password1 and password2 are the same
            self.request.user.set_password(form.cleaned_data['password1'])
            self.request.user.save()
            ## OK, go to success_url
            return super(ForgotPasswordView, self).form_valid(form)
        ## token is None, ask for email to send
        try:
            for_user = User.objects.get(**form.cleaned_data)
        except User.DoesNotExist:
            form.errors.update({'invalid': _("No user with this e-mail. Are you registered ?")})
        except User.DoesNotExist:
            form.errors.update({'invalid': _("More users with this e-mail. Are you registered more times ?")})
        if form.is_valid():
            try:
                fullname = for_user.get_profile().fullname
            except:
                fullname = "%s %s" % (for_user.first_name, for_user.last_name)
            context = { 'fullname': fullname, 'username': for_user.username }
            token = default_token_generator.make_token(for_user)
            for_user.get_profile().token = token
            for_user.get_profile().save()
            ## we have to send an email using SendMail
            context.update({'protocol': self.protocol_for_link, 'domain': get_current_site(self.request).domain, 'site_name': get_current_site(self.request).name})
            context.update({'resetpasswordlinkpath': reverse('resetpasswd', kwargs={'token': token})})
            context_for_mail = { 'type': self.send_mail_type_name, 'mailto': [for_user.email], 'smtp_host': getattr(settings, 'EMAIL_HOST', 'localhost') }
            context_for_mail.update({ for_user.email : context })

            nsent = SendTypeMail(context_for_mail) ## TODO: catch exceptions
            context.update({'nsent':nsent})
            return TemplateResponse(self.request, self.success_template_name, context=context)
        ## which user have this mail ??? retry !
        return self.form_invalid(form)

    def get(self, request, *args, **kw):
        # if user is authenticated ??? redirect to change password
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse("chpasswd"))

        if self.token is None:
            self.token = self.kwargs.get(self.slug_field, None)

        if self.token is not None:
            user = authenticate(token=self.token)
            if user is not None:
                if user.is_active:
                    auth_login(self.request, user)
            else:
                self.token = None
            if self.delete_token_after_use:
                try:
                    user.get_profile().token = None
                    user.get_profile().save()
                except:
                    pass

        return super(ForgotPasswordView, self).get(request, *args, **kw)
