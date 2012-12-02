# pylint: disable-msg=C0301,C0103,W0201,W0212,E1101
# pep8: ignore=E201
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# views.py -- python module for auth management
#
# Copyright (C) 2012 Aderit srl
#
# Author: Marco Bardelli <marco.bardelli@aderit.it>, <bardelli.marco@gmail.com>
#
# This file is part of DjangoContribAderit.
#
# DjangoContribAderit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DjangoContribAderit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DjangoContribAderit.  If not, see <http://www.gnu.org/licenses/>.
'''Authentication and user profile views (controllers)'''

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
from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.forms import (fields as forms_fields,
                          widgets as forms_widgets,
                          forms as forms_forms)
from django.views.generic.base import TemplateView as _TemplateView
from django.views.generic.detail import DetailView as _DetailView
from django.views.generic.edit import (UpdateView as _UpdateView,
                                       CreateView as _CreateView,
                                       FormView as _FormView)
from django.utils.translation import ugettext as _
from django.utils.log import getLogger

from django.contrib.sites.models import get_current_site
from django.contrib.auth import (authenticate, login as auth_login,
                                 logout as auth_logout, REDIRECT_FIELD_NAME)
from django.contrib.auth.models import User
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UserChangeForm, AdminPasswordChangeForm,
                                       PasswordChangeForm, PasswordResetForm)
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.tokens import default_token_generator

from django.contrib.aderit.generic_utils.views import \
    (GenericUtilView, GenericProtectedView, GenericProtectedUncacheableView)
from django.contrib.aderit.generic_utils.forms import \
    generic_formclass_factory, SortedDict
from django.contrib.aderit.send_mail import SendTypeMail
from django.contrib.aderit.access_account import \
    _get_model_from_auth_profile_module
from django.contrib.aderit.access_account.tokens import \
    (make_random_expirable_token, make_random_unexpirable_token)

## SignupView settings
DO_LOGIN_AFTER_SIGNUP = \
    getattr(settings, 'ACCESS_ACCOUNT_LOGIN_ON_SIGNUP', False)
SIGNUP_USER_IS_ACTIVE = \
    getattr(settings, 'ACCESS_ACCOUNT_SIGNUP_USER_IS_ACTIVE', True)
## LoginView settings
ALLOW_LOGIN_TO_AUTHENTICATED = \
    getattr(settings, 'ACCESS_ACCOUNT_ALLOW_LOGIN_TO_AUTHENTICATED', False)
ALLOW_LOGIN_VIA_TOKEN = \
    getattr(settings, 'ACCESS_ACCOUNT_ALLOW_LOGIN_VIA_TOKEN', False)
## LoginView and ForgotPasswordView settings
DELETE_TOKEN_AFTER_USE = \
    getattr(settings, 'ACCESS_ACCOUNT_DELETE_TOKEN_AFTER_USE', True)
## LogoutView settings
CLEAN_COOKIES_ON_LOGOUT = \
    getattr(settings, 'ACCESS_ACCOUNT_CLEAN_COOKIES_ON_LOGOUT', True)
## ForgotPasswordView settings
USE_DB_FOR_TOKEN = \
    getattr(settings, 'ACCESS_ACCOUNT_USE_DB_FOR_TOKEN', True)
USE_EXPIRABLE_TOKEN = \
    getattr(settings, 'ACCESS_ACCOUNT_USE_EXPIRABLE_TOKEN', True)

## maybe in CaptchableView
HAS_CAPTCHA = 'captcha' in settings.INSTALLED_APPS
USE_CAPTCHA_SIGNUP = HAS_CAPTCHA and getattr(settings, 'CAPTCHA_SIGNUP', True)
USE_CAPTCHA_CHPSW = HAS_CAPTCHA and getattr(settings, 'CAPTCHA_CHPSW', False)
USE_CAPTCHA_CHPROFILE = HAS_CAPTCHA and \
    getattr(settings, 'CAPTCHA_CHPROFILE', False)
USE_CAPTCHA_FORGOTPSW = HAS_CAPTCHA and \
    getattr(settings, 'CAPTCHA_FORGOTPSW', True)
USE_CAPTCHA_RESETPSW = HAS_CAPTCHA and \
    getattr(settings, 'CAPTCHA_RESETPSW', False)
if HAS_CAPTCHA:
    from captcha.fields import CaptchaField
CAPTCHA_FIELD_CLASS = (HAS_CAPTCHA and CaptchaField) or None

logger = getLogger('aderit.access_account.views')


def _try_callback(instanceview, attr_name_for_callback):
    _callback = getattr(instanceview, attr_name_for_callback, None)
    if _callback is None:
        return
    if isinstance(_callback, basestring):
        _callback = getattr(instanceview, _callback, _callback)
    if callable(_callback):
        if type(_callback).__name__ == 'instancemethod':
            _callback()
        elif type(_callback).__name__ == 'function':
            _callback(instanceview)
    return


def _consume_formfields(list_, *args):
    for f in args:
        try:
            list_.pop(list_.index(f))
        except ValueError:
            pass


def _maybe_add_captcha(self, actual_fields):
    if self.use_captcha and HAS_CAPTCHA and \
            self.captcha_field_class is not None:
        if self.captcha_field is None:
            self.captcha_field = \
                self.captcha_field_class(label=_("Inserire Captcha"),
                                         help_text=_("(obbligatorio la per"
                                                     " sicurezza)"))
        actual_fields.update({self.captcha_field_name: self.captcha_field})


class CaptchableView(GenericProtectedView):
    use_captcha = False
    captcha_field_class = CAPTCHA_FIELD_CLASS
    captcha_field_name = 'captcha'
    captcha_field = None


class LoginView(_FormView, CaptchableView):
    """
    Class based view, copied from django.contrib.auth.views.login

    Displays the login form and handles the login action.
    """
    model = _get_model_from_auth_profile_module()
    template_name = 'registration/login_as_ul.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    ## TODO: figure out how to use success_url
    redirect_to = getattr(settings, 'LOGIN_REDIRECT_URL', "")
    current_app = None
    authentication_form_class = AuthenticationForm
    formfields_uniqueness = False
    allow_login_to_authenticated = ALLOW_LOGIN_TO_AUTHENTICATED
    allow_token = ALLOW_LOGIN_VIA_TOKEN
    delete_token_after_use = DELETE_TOKEN_AFTER_USE
    token = None
    token_field = 'token'
    model_token_field_name = 'token'
    after_login_callback = None

    def setup_attrs(self, **kwargs):
        self.redirect_to = self.request.REQUEST.get(self.redirect_field_name,
                                                    self.redirect_to)

        netloc = urlparse(self.redirect_to)[1]
        if netloc and netloc != self.request.get_host():
            self.redirect_to = getattr(settings, 'LOGIN_REDIRECT_URL', "")

        super(LoginView, self).setup_attrs(**kwargs)

        if self.token is None and self.token_field != 'token':
            self.token = kwargs.get(self.token_field, None)

        if not self.allow_token:
            self.token = None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated() and \
                not self.allow_login_to_authenticated:
            return HttpResponseRedirect(self.redirect_to)

        if self.token is not None:
            user = authenticate(token=self.token)
            logger.debug("user %s, token: %s", user, self.token)
            if user is not None:
                if user.is_active:
                    auth_login(self.request, user)
                    _try_callback(self, 'after_login_callback')
                else:
                    self.token = None
            else:
                self.token = None
            if self.delete_token_after_use:
                try:
                    user.get_profile().token = None
                    user.get_profile().save()
                except:
                    self.token = None

        if self.token is None:
            return super(LoginView, self).get(request, *args, **kwargs)
        else:
            assert(self.request.user.is_authenticated())
            return HttpResponseRedirect(self.redirect_to)

    def get_initial(self):
        initial = super(LoginView, self).get_initial()
        initial.update({self.redirect_field_name: self.redirect_to})
        return initial

    def get_form_class(self):
        if self.form_class is not None:
            return super(LoginView, self).get_form_class()

        additional_fields = SortedDict()
        # add input hidden for redirection
        next_field = forms_fields.CharField(widget=forms_widgets.HiddenInput)
        additional_fields.update({self.redirect_field_name: next_field})

        _maybe_add_captcha(self, additional_fields)

        uniqueness = self.formfields_uniqueness
        base = self.authentication_form_class
        return generic_formclass_factory([], fields_uniqueness=uniqueness,
                                         bases=[base],
                                         sorted_fields=additional_fields)

    ## POST related mathod
    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        _try_callback(self, 'after_login_callback')

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
                                           self.redirect_field_name:
                                           self.redirect_to,
                                           'site': current_site,
                                           'site_name': current_site.name})
        return TemplateResponse(self.request, self.template_name, context,
                                current_app=self.current_app)


class UpdateView(_UpdateView, CaptchableView):
    model = _get_model_from_auth_profile_module()
    slug = None
    exclude_formfields = ['user', 'password', 'user_permissions',
                          'is_staff', 'is_superuser', 'is_active',
                          'groups', 'last_login', 'date_joined']
    additional_exclude_formfields = None
    user_change_form_class = UserChangeForm
    formfields_uniqueness = False
    require_formfields = None
    after_update_profile_callback = None

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return ""

    def get_form_class(self):
        if self.form_class is not None:
            return super(UpdateView, self).get_form_class()

        super_form_k = super(UpdateView, self).get_form_class()
        super_form_k.base_fields = {}
        _sorted_fields = self.user_change_form_class.base_fields
        _uniqueness = self.formfields_uniqueness
        form_k = generic_formclass_factory([], sorted_fields=_sorted_fields,
                                           prepend_fields=True,
                                           fields_uniqueness=_uniqueness,
                                           bases=[super_form_k])

        _exclude_formfields = self.exclude_formfields[:]
        if self.additional_exclude_formfields is not None:
            _exclude_formfields += self.additional_exclude_formfields[:]
        for k in _exclude_formfields:
            if k in form_k.base_fields:
                del form_k.base_fields[k]

        if self.require_formfields is not None:
            for k in self.require_formfields:
                if k in form_k.base_fields and \
                        hasattr(form_k.base_fields[k], 'required') and \
                        not getattr(form_k.base_fields[k], 'required'):
                    form_k.base_fields[k].required = True

        _maybe_add_captcha(self, form_k.base_fields)

        return form_k

    def get_initial(self):
        if self.object is None:
            return {}
        initial = {}
        rel_fields = []
        for f in self.object._meta.fields:
            if f.rel:
                rel_fields.insert(0, f)
                continue
            initial.update({f.name: getattr(self.object, f.name)})
        ## Too much invasive, should respect concrete model properties.
        ## Also have to prefix according with
        ## get_form_class / generic_formclass_factory
        for rel_f in rel_fields:
            related_obj = getattr(self.object, rel_f.name)
            for f in related_obj._meta.fields:
                if f.name in initial:
                    initial.update({rel_f.name + "_" + f.name:
                                    getattr(related_obj, f.name)})
                else:
                    initial.update({f.name: getattr(related_obj, f.name)})
        return initial

    def get_object(self, queryset=None):
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        try:
            account = self.model.objects.get(**{self.slug_field: self.slug})
        except (self.model.DoesNotExist, AttributeError):
            account = None
        ### TODO: rewite in a simpler way
        try:
            current_account = self.request.user.get_profile()
        except (self.model.DoesNotExist, AttributeError):
            current_account = None
        if (self.request.user.is_superuser and self.slug) or \
                (current_account is not None) and (account == current_account):
            return account
        try:
            return self.request.user.get_profile()
        except (self.model.DoesNotExist, AttributeError):
            return None

    ## POST related method
    def form_valid(self, form):
        ### TODO: put interesting fields in an instance variable list
        if self.object is None:
            return redirect_to_login(self.request.path)
        if form.has_changed():
            for k, v in form.data.items():
                if not k in form.changed_data:
                    continue
                if k in [f.name for f in self.model._meta.fields
                         if not f.name in ['id', 'pk', 'user', 'user_id']]:
                    setattr(self.object, k, v)
                elif k in [f.name for f in self.object.user._meta.fields
                           if not f.name in ['id', 'pk']]:
                    setattr(self.object.user, k, v)
            self.object.save()
            _try_callback(self, 'after_update_profile_callback')
        return HttpResponseRedirect(self.get_success_url())


class SignupView(_CreateView, GenericProtectedUncacheableView, CaptchableView):
    model = _get_model_from_auth_profile_module()
    template_name = "registration/signup_as_ul.html"
    user_create_form_class = UserCreationForm
    formfields_uniqueness = False
    exclude_formfields = ['user', 'password', 'user_permissions',
                          'is_staff', 'is_superuser', 'is_active',
                          'groups', 'last_login', 'date_joined']
    additional_exclude_formfields = None
    require_formfields = None
    login_after_signup = DO_LOGIN_AFTER_SIGNUP
    signup_user_is_active = SIGNUP_USER_IS_ACTIVE
    slug = None
    success_url = "/"
    after_signup_callback = None

    def get_initial(self):
        return {}

    def get_form_class(self):
        if self.form_class is not None:
            return super(SignupView, self).get_form_class()

        super_form_k = super(SignupView, self).get_form_class()
        _uniqueness = self.formfields_uniqueness
        form_k = generic_formclass_factory([super_form_k, User],
                                           fields_uniqueness=_uniqueness,
                                           bases=[self.user_create_form_class])
        _exclude_formfields = self.exclude_formfields[:]
        if self.additional_exclude_formfields is not None:
            _exclude_formfields += self.additional_exclude_formfields[:]
        for k in _exclude_formfields:
            if k in form_k.base_fields:
                del form_k.base_fields[k]

        if self.require_formfields is not None:
            for k in self.require_formfields:
                if k in form_k.base_fields and \
                        hasattr(form_k.base_fields[k], 'required') and \
                        not getattr(form_k.base_fields[k], 'required'):
                    form_k.base_fields[k].required = True

        _maybe_add_captcha(self, form_k.base_fields)

        return form_k

    def form_valid(self, form):
        form_keys = form.data.keys()[:]
        new_user = User.objects.create_user(username=form.data['username'],
                                            password=form.data['password1'],
                                            email=form.data.get('email', None))
        # consume username, password1 password2, email pk id user
        _user_related_to_consume = ['username', 'password1', 'password2',
                                    'email', 'password']
        _user_related_to_consume += ['last_login', 'date_joined']
        _consume_formfields(form_keys, *_user_related_to_consume)
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        account_kwargs = {}
        _model_field_names = [f.name for f in self.model._meta.fields
                              if not f.name in ['pk', 'id', 'user']]
        _consume_formfields(form_keys, 'pk', 'id', 'user')
        for fname in form_keys[:]:
            if fname in _model_field_names:
                account_kwargs.update({fname: form.data[fname]})
                _consume_formfields(form_keys, fname)
        try:
            self.object = new_user.get_profile()
        except (self.model.DoesNotExist, AttributeError):
            self.object = self.model(user=new_user, **account_kwargs)
            self.object.save()
        else:
            rows = self.model.objects\
                .filter(pk=self.object.pk).update(**account_kwargs)
            assert(rows == 1 or rows == len(account_kwargs) == 0)

        have_to_save = False
        if bool(form_keys):  # remain some keys try them over User model
            for k in form_keys[:]:
                if hasattr(new_user, k):
                    have_to_save = True
                    setattr(new_user, k, form.data[k])
                    _consume_formfields(form_keys, k)

        if not self.signup_user_is_active:
            new_user.is_active = False
            have_to_save = True
        if have_to_save:
            new_user.save()
        if bool(form_keys):
            logger.warning("remain some unused form fields: %s", form_keys)

        if self.login_after_signup and new_user.is_active:
            u = authenticate(username=form.data['username'],
                             password=form.data['password1'])
            auth_login(self.request, u)

        self.new_user = new_user
        _try_callback(self, 'after_signup_callback')
        delattr(self, 'new_user')
        return HttpResponseRedirect(self.get_success_url())


class ChangePasswordView(_FormView, GenericProtectedUncacheableView,
                         CaptchableView):
    model = _get_model_from_auth_profile_module()
    slug = None
    slug_field = 'id'
    password_change_form_class = PasswordChangeForm
    admin_password_change_form_class = AdminPasswordChangeForm
    change_done_template_name = 'account/chpsw.html'
    after_change_password_callback = None

    def get_initial(self):
        # initially always empty form
        return {}

    def get_form_class(self):
        if self.request.user.is_superuser:
            return self.admin_password_change_form_class
        return self.password_change_form_class

    def get_form(self, form_class):
        logger.debug("Form for current user: %s",
                     form_class(self.request.user).as_p())
        if self.slug is None:
            return form_class(self.request.user, **self.get_form_kwargs())
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        try:
            account = self.model.objects.get(**{self.slug_field: self.slug})
            if not (self.request.user.is_superuser or
                    self.request.user == account.user):
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
        _try_callback(self, 'after_change_password_callback')
        return TemplateResponse(self.request, self.change_done_template_name)


class ForgotPasswordView(_FormView, CaptchableView):
    success_template_name = 'account/forgot_psw_ok.html'
    send_mail_type_name = 'forgot password'
    named_url = 'forgotpsw'
    delete_token_after_use = DELETE_TOKEN_AFTER_USE
    token = None
    token_field = 'token'
    success_url = '/'
    protocol_for_link = 'http'
    change_password_named_url = "chpasswd"
    authenticated_goto_change_password = True
    use_db_for_token = USE_DB_FOR_TOKEN
    use_expirable_token = USE_EXPIRABLE_TOKEN

    def setup_attrs(self, **kwargs):
        super(ForgotPasswordView, self).setup_attrs(**kwargs)
        if self.token is None and self.token_field != 'token':
            self.token = kwargs.get(self.token_field, None)

    def get_initial(self):
        if self.request.user.is_authenticated():
            return {'email': self.request.user.email}
        return {}

    def get_form_class(self):
        if self.token is not None and self.request.user.is_authenticated():
            ## here, from link in email sent yet
            return generic_formclass_factory(AdminPasswordChangeForm)
        if self.request.user.is_authenticated() and \
                not self.authenticated_goto_change_password:
            return generic_formclass_factory(AdminPasswordChangeForm)
        ## token is None, ask for email to send
        return generic_formclass_factory(PasswordResetForm)

    def form_valid(self, form):
        if self.token is not None and \
                isinstance(form, AdminPasswordChangeForm):
            ### form is valid, password1 and password2 are the same
            self.request.user.set_password(form.cleaned_data['password1'])
            self.request.user.save()
            ## OK, go to success_url
            return super(ForgotPasswordView, self).form_valid(form)
        ## token is None, ask for email to send
        try:
            for_user = User.objects.get(**form.cleaned_data)
        except User.DoesNotExist:
            err = _("No user with this e-mail. Are you registered ?")
            form._errors[forms_forms.NON_FIELD_ERRORS] = \
                form.error_class([err])
        except User.MultipleObjectsReturned:
            err = _("More users with this e-mail. "
                    "Are you registered more times ? "
                    "Contacts the site administrator, please")
            form._errors[forms_forms.NON_FIELD_ERRORS] = \
                form.error_class([err])

        if form.is_valid():
            try:
                fullname = for_user.get_profile().fullname
            except:
                fullname = "%s %s" % (for_user.first_name, for_user.last_name)
            context = {'fullname': fullname, 'username': for_user.username}
            if self.use_db_for_token:
                if self.use_expirable_token:
                    token = make_random_expirable_token()
                else:
                    token = make_random_unexpirable_token()
                for_user.get_profile().token = token
                for_user.get_profile().save()
            else:
                token = default_token_generator.make_token(for_user)

            ## we have to send an email using SendMail
            context.update({
                'protocol': self.protocol_for_link,
                'domain': get_current_site(self.request).domain,
                'site_name': get_current_site(self.request).name
            })
            _linkpath = "%s%s/" % (reverse(self.named_url), token)
            context.update({'resetpasswordlinkpath': _linkpath})
            _link = "%s://%s%s" % (context['protocol'],
                                   context['domain'],
                                   context['resetpasswordlinkpath'])
            context.update({'link': _link})
            context_for_mail = {'type': self.send_mail_type_name,
                                'mailto': [for_user.email],
                                'smtp_host': getattr(settings,
                                                     'EMAIL_HOST',
                                                     'localhost')}
            context_for_mail.update({for_user.email: context})

            nsent = 0
            try:
                nsent = SendTypeMail(context_for_mail)
            except ObjectDoesNotExist, exc:
                logger.critical("SendMail of type '%s', does not exist: %s",
                                self.send_mail_type_name, exc)
            context.update({'nsent': nsent})
            return TemplateResponse(self.request,
                                    self.success_template_name,
                                    context=context)
        ## which user have this mail ??? retry !
        return self.form_invalid(form)

    def get(self, request, *args, **kw):
        # if user is authenticated ??? redirect to change password
        if self.request.user.is_authenticated() and \
                self.authenticated_goto_change_password:
            _reversed = reverse(self.change_password_named_url)
            return HttpResponseRedirect(_reversed)

        if self.token is not None:
            user = authenticate(token=self.token)
            if user is not None:
                if user.is_active:
                    auth_login(self.request, user)
                    logger.debug("Forgot: auth via token OK! -"
                                 "- delete: %s use_db: %s",
                                 self.delete_token_after_use,
                                 self.use_db_for_token)
                else:
                    self.inactive_user = user

                if self.delete_token_after_use and self.use_db_for_token:
                    try:
                        user.get_profile().token = ""
                        user.get_profile().save()
                    except Exception, exc:
                        logger.error("Exc: %s -- %s %s", exc,
                                     self.delete_token_after_use,
                                     self.use_db_for_token)
            else:
                self.invalid_token = self.token
                self.token = None

        if hasattr(self, 'invalid_token'):
            ## TODO: may be advise ???
            delattr(self, 'invalid_token')
        if hasattr(self, 'inactive_user'):
            ## TODO: may be advise ???
            assert(not self.inactive_user.is_active)
            delattr(self, 'inactive_user')
        return super(ForgotPasswordView, self).get(request, *args, **kw)


################## Without Form Views
class LogoutView(_TemplateView, GenericUtilView):
    """
    Class based view, copied from django.contrib.auth.views.logout

    Log out the user and displays 'You are logged out' message.
    """
    template_name = 'registration/logged_out.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_to = None
    current_app = None
    next_page = None
    clean_response_cookies = CLEAN_COOKIES_ON_LOGOUT
    after_logout_callback = None

    def get(self, request, *args, **kwargs):
        auth_logout(self.request)
        _try_callback(self, 'after_logout_callback')
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


class DetailView(_DetailView, GenericUtilView):
    slug_field = 'pk'

    def get_object(self, queyset=None):
        if self.model is None:
            self.model = _get_model_from_auth_profile_module()
        if self.kwargs.get('slug', None) is None and \
                self.request.user.is_authenticated():
            try:
                return self.request.user.get_profile()
            except (self.model.DoesNotExist, AttributeError):
                return None
        try:
            return self.model.objects.get(**{self.slug_field:
                                             self.kwargs.get('slug', None)})
        except:
            return None
