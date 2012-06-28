# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.views.generic import TemplateView, CreateView
from django.views.generic.edit import FormView, ProcessFormView
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.http import HttpResponseRedirect
from django.forms import ModelForm, Form
from django.forms import fields as form_fields
from django.contrib.aderit.access_account.models import AccessAccount, ResettablePassword
from django.shortcuts import render_to_response
from django.template import RequestContext
import logging
from captcha.fields import CaptchaField
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import os, re, time
from django.contrib.aderit.generic_utils.currentUserMiddleware import get_current_user
import datetime
from datetime import datetime, timedelta, date
from lxml import etree
from django.contrib.aderit.send_mail.views import SendTypeMail
from django.contrib.aderit.generic_utils.templatetags.nice_name import nice_name

log = logging.getLogger('django.debug')
log.addHandler(logging.StreamHandler())
log.handlers[0].setFormatter(logging.Formatter("%(name)s:%(levelname)s: %(message)s"))
log.setLevel(logging.DEBUG)

#################### with only Class-based View

def is_only_numbers(stringa):
    if re.match("^[0-9]+$",stringa):
	return True
    else:
	return False

class CondizioniForm(Form):
    accetto = forms.BooleanField(label="*Accetto i Termini e le Condizioni", 
				help_text="<a id='termini' href='#termini'><u>(clicca per visualizzare)</u></a>", 
				required=True)

class CaptchaForm(Form):
    captcha = CaptchaField(label="*Inserire Captcha", help_text = "(obbligatorio la per sicurezza)") 

class ForgotPswUsernameForm(Form):
    username = forms.RegexField(label="Username", max_length=125, regex=r'^[\w\s]+', required=True,
                                help_text = "(inserire il proprio username)",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})

    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get("username")
	if not username:
	    username = "Utente non inserito"
        user = User.objects.filter(username=username)


        if len(user) == 0:
            msg = u"Il campo inserito non corrisponde a nessun account presente nel sistema"
            self._errors["username"] = self.error_class([msg])
        else:
            if not user[0].email:
                msg = u"Il campo inserito corrisponde ad un account presente nel sistema, ma non e' dotato di email quindi non e' possibile effettuare il reset della password, prego contattare gli amministratori di sistema"
                self._errors["username"] = self.error_class([msg])
	    
class AccessAccountProfileForm(Form):
    nickname = forms.RegexField(label="*Username", max_length=125, regex=r'^[\w\s]+',
                                help_text = "(da usare come username per il login)",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    first_name = forms.RegexField(label="*Nome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    last_name = forms.RegexField(label="*Cognome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    email = forms.EmailField(label="*Email", help_text = "(inserire la mail di lavoro)", max_length=125)
    phone = forms.CharField(label="Telefono Fisso",  required=False,
                                help_text = "(il numero telefonico dell'ufficio, non usare punteggiatura)")
    phone_mobile = forms.CharField(label="Telefono Mobile", required=False,
                                help_text = "(il numero cellulare, non usare punteggiatura)")
    company = forms.CharField(label="Ragione Sociale", max_length=125, required=False,
                                help_text = "(il nome dell'azienda per cui lavora)")
    address = forms.CharField(label="Indirizzo", max_length=125, required=False,
                                help_text = "(indirizzo di fatturazione)")
    cap = forms.CharField(label="CAP", required=False,
                                help_text = "(il cap associato all'indirizzo)")
    location = forms.CharField(label="Localita'", max_length=125, required=False,
                                help_text = "(la localita' presso cui si lavora)")
    paese = forms.CharField(label="Paese", max_length=125, required=False,
                                help_text = "(il paese presso cui si lavora)")
    partita_iva = forms.CharField(label="Partita Iva", max_length=125, required=False,
                                help_text = "(partita iva)")

    def clean(self):
        cleaned_data = self.cleaned_data
        company = cleaned_data.get("company")
        partita_iva = cleaned_data.get("partita_iva")
        address = cleaned_data.get("address")
        cap = cleaned_data.get("cap")
        phone = cleaned_data.get("phone")
        phone_mobile = cleaned_data.get("phone_mobile")
        location = cleaned_data.get("location")
        paese = cleaned_data.get("paese")

        if phone:
	    if not is_only_numbers(phone):
                msg = u"Inserire correttamente il numero telefonico"
                self._errors["phone"] = self.error_class([msg])

        if phone_mobile:
	    if not is_only_numbers(phone_mobile):
                msg = u"Inserire correttamente il numero telefonico mobile"
                self._errors["phone_mobile"] = self.error_class([msg])
        if cap:
	    if not is_only_numbers(cap):
                msg = u"Inserire correttamente il cap"
                self._errors["cap"] = self.error_class([msg])
		

class AccessAccountSignupForm(Form):
    nickname = forms.RegexField(label="*Username", max_length=125, regex=r'^[\w\s]+',
                                help_text = "(da usare come username per il login)",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    first_name = forms.RegexField(label="*Nome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    last_name = forms.RegexField(label="*Cognome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    email = forms.EmailField(label="*Email", help_text = "(inserire la mail di lavoro)", max_length=125)
    phone = forms.CharField(label="Telefono Fisso", required=False,
                                help_text = "(il numero telefonico dell'ufficio, non usare punteggiatura)")
    phone_mobile = forms.CharField(label="Telefono Mobile", required=False,
                                help_text = "(il numero cellulare, non usare punteggiatura)")
    password = forms.CharField(label="*Password", widget=forms.PasswordInput, max_length=30,
                                help_text = "(usare una password sicura, contenente numeri e lettere)")
    password_confirm = forms.CharField(label="*Password confirmation", widget=forms.PasswordInput, max_length=30,
                                help_text = "(inserire la stessa password per verifica)")
    company = forms.CharField(label="Ragione Sociale", max_length=125, required=False,
                                help_text = "(il nome dell'azienda per cui lavora)")
    address = forms.CharField(label="Indirizzo", max_length=125, required=False,
                                help_text = "(indirizzo di fatturazione)")
    cap = forms.CharField(label="CAP", required=False,
                                help_text = "(il cap associato all'indirizzo)")
    location = forms.CharField(label="Localita'", max_length=125, required=False,
                                help_text = "(la localita' presso cui si lavora)")
    paese = forms.CharField(label="Paese", max_length=125, required=False,
                                help_text = "(il paese presso cui si lavora)")
    partita_iva = forms.CharField(label="Partita Iva", max_length=125, required=False,
                                help_text = "(partita iva)")

    def clean(self):
        cleaned_data = self.cleaned_data
        psw1 = cleaned_data.get("password")
        psw2 = cleaned_data.get("password_confirm")
        email = cleaned_data.get("email")
        nickname = cleaned_data.get("nickname")
        company = cleaned_data.get("company")
        cap = cleaned_data.get("cap")
        phone = cleaned_data.get("phone")
        phone_mobile = cleaned_data.get("phone_mobile")
        location = cleaned_data.get("location")
        paese = cleaned_data.get("paese")
        partita_iva = cleaned_data.get("partita_iva")
        address = cleaned_data.get("address")

        if phone:
            if not is_only_numbers(phone):
                msg = u"Inserire correttamente il numero telefonico"
                self._errors["phone"] = self.error_class([msg])

        if phone_mobile:
            if not is_only_numbers(phone_mobile):
                msg = u"Inserire correttamente il numero telefonico mobile"
                self._errors["phone_mobile"] = self.error_class([msg])
        if cap:
            if not is_only_numbers(cap):
                msg = u"Inserire correttamente il cap"
                self._errors["cap"] = self.error_class([msg])


        if len(User.objects.filter(username=nickname)) > 0:
            msg = u"Utente gia' esistente"
            self._errors["nickname"] = self.error_class([msg])
            del cleaned_data["nickname"]

        if psw1 != psw2:
            msg = u"Password differenti"
            self._errors["password_confirm"] = self.error_class([msg])

        # Always return the full collection of cleaned data.
        return cleaned_data


class ResetPswForm(Form):
    password_new = forms.CharField(label="*Nuova Password", widget=forms.PasswordInput, max_length=30,
                                help_text = "(inserire la nuova password)")
    password_new_confirm = forms.CharField(label="*Conferma nuova Password", widget=forms.PasswordInput, max_length=30,
                                help_text = "(reinserire la nuova password, per conferma)",
                                error_messages = {'invalid': "Password Check errato"})

    def clean(self):
        cleaned_data = self.cleaned_data
        psw1 = cleaned_data.get("password_new")
        psw2 = cleaned_data.get("password_new_confirm")

        if psw1 != psw2:
            msg = u"Password differenti"
            self._errors["password_new_confirm"] = self.error_class([msg])

        return cleaned_data


class ChPsw(Form):
    password_old = forms.CharField(label="*Vecchia Password", widget=forms.PasswordInput, 
                                help_text = "(inserire la vecchia password)",
                                error_messages = {'invalid': "Password errata"})
    password_new = forms.CharField(label="*Nuova Password", widget=forms.PasswordInput, max_length=30,
                                help_text = "(inserire la nuova password)")
    password_new_confirm = forms.CharField(label="*Conferma nuova Password", widget=forms.PasswordInput, max_length=30,
                                help_text = "(reinserire la nuova password, per conferma)",
                                error_messages = {'invalid': "Password Check errato"})

    def clean(self):
        cleaned_data = self.cleaned_data
        user = get_current_user()
        psw = cleaned_data.get("password_old")
        psw1 = cleaned_data.get("password_new")
        psw2 = cleaned_data.get("password_new_confirm")

        if not psw:
            msg = u"Vecchia password obbligatoria"
            self._errors["password_old"] = self.error_class([msg])

        if not user.check_password(psw):
            msg = u"Reinserire vecchia password"
            self._errors["password_old"] = self.error_class([msg])

        if psw1 != psw2:
            msg = u"Password differenti"
            self._errors["password_new_confirm"] = self.error_class([msg])
            
        # Always return the full collection of cleaned data.
        return cleaned_data


class AccessAccountControlSubscription(FormView):
    use_captcha = getattr(settings,'ACCESS_ACCOUNT_USE_CAPTCHA',True)

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
        ##log.debug("get_form_class ([%s])|%s %s", self.form_class, self.request.method, self.request.path)
        # Qui controllo qualcosa e scelgo
        # volendo eseguendo qualche metodo per preparare gli attributi etc ...
        if not self.form_class is None:
            val = super(AccessAccountControlSubscription, self).get_form_class()
            ##log.debug("get_form_class return: %s", val)
            return val
        
        name = None
        attrs = {}
        if not self.request.user.is_authenticated() and self.signup:
	    if self.use_captcha:
                form_k = type(name or 'SignupForm1', (AccessAccountSignupForm,CaptchaForm,CondizioniForm), attrs)
	    else:
                form_k = type(name or 'SignupForm1', (AccessAccountSignupForm,CondizioniForm), attrs)
            #log.debug("get_form_class dir(): %s", form_k)
            return form_k

        if self.request.user.is_authenticated() and self.chpsw:
	    if self.use_captcha:
                form_k = type(name or 'ChPswForm1', (ChPsw,CaptchaForm), attrs)
	    else:
                form_k = type(name or 'ChPswForm1', (ChPsw,), attrs)
            #log.debug("get_form_class dir(): %s", form_k)
            return form_k

        if self.request.user.is_authenticated() and self.chprofile:
	    if self.use_captcha:
                form_k = type(name or 'ChProfileForm1', (AccessAccountProfileForm,CaptchaForm,CondizioniForm), attrs)
            else:
                form_k = type(name or 'ChProfileForm1', (AccessAccountProfileForm,CondizioniForm), attrs)
            #log.debug("get_form_class dir(): %s", form_k)
            return form_k

        if not self.request.user.is_authenticated() and self.forgotpsw:
	    if self.use_captcha:
                form_k = type(name or 'ForgotPswForm1', (ForgotPswUsernameForm,CaptchaForm,), attrs)
	    else:
                form_k = type(name or 'ForgotPswForm1', (ForgotPswUsernameForm,), attrs)
            #log.debug("get_form_class dir(): %s", form_k)
            return form_k
           
        if not self.request.user.is_authenticated() and self.resetpsw:
	    if self.use_captcha:
                form_k = type(name or 'ResetPswForm1', (ResetPswForm,CaptchaForm,), attrs)
	    else:
                form_k = type(name or 'ResetPswForm1', (ResetPswForm,), attrs)
            #log.debug("get_form_class dir(): %s", form_k)
            return form_k

        #log.debug("get_form_class user is authenticated: %s", self.request.user.is_authenticated())
        if self.request.user.is_authenticated():
            return Form

        return AuthenticationForm
    
    def get_context_data(self, **kwargs):
        from django.template import RequestContext
        #from sekizai.context import SekizaiContext
        kwargs.update({'signup':self.signup , 'chpsw':self.chpsw, 'chprofile':self.chprofile, 'forgotpsw':self.forgotpsw, 'resetpsw':self.resetpsw}) 
        #log.debug("get_context_data (kw: %s)|%s %s", kwargs, self.request.method, self.request.path)
        super_context = super(AccessAccountControlSubscription, self).get_context_data(**kwargs)
        context = RequestContext(self.request, super_context)
        #log.debug("get_context_data return: %s", super_context)
        return context

    def get_success_url(self):
        #log.debug("get_success_url ()|%s %s", self.request.method, self.request.path)
        try:
            val = None
            val = super(AccessAccountControlSubscription, self).get_success_url()
        except:
            val = HttpResponseRedirect(".")
        #log.debug("get_success_url return: %s", val)
        #return val
        if self.signup:
            return reverse('profile') + "?changed=True"
        if self.chpsw:
            return reverse('profile') + "?changed=True"
        if self.chprofile:
            return reverse('profile') + "?changed=True"
        if self.forgotpsw:
            return reverse('forgotpsw') + "?changed=True"
        if self.resetpsw:
            return reverse('resetpsw') + "?changed=True"
        return val

    def form_valid(self, form):
        #log.debug("form_valid (f: %s)| %s %s", form, self.request.method, self.request.path)
        val = super(AccessAccountControlSubscription, self).form_valid(form)
        #log.debug("form_valid return: %s", val)
        #log.debug("form_valid The Form is: %s", self.request.POST)
        self.form_is_valid = True
        return val

    def form_invalid(self, form):
        #log.debug("form_invalid (f: %s)|%s %s", form, self.request.method, self.request.path)
        val = super(AccessAccountControlSubscription, self).form_invalid(form)
        #log.debug("form_invalid return: %s", val)
        self.form_is_valid = False
        return val

    def render_to_response(self, context, **response_kwargs):
        #log.debug("render_to_response (kw: %s) -- self.response_class: %s", response_kwargs, self.response_class)
        #log.debug("render_to_response: %s %s", self.request.method, self.request.path)
        t = self.response_class(self.request, self.get_template_names(), context)
        val = t.render()
        #log.debug("render values: %s", self.__dict__)
        #log.debug("render_to_response return: %s is rendered: %s", type(t), t.is_rendered)
        del t 
        return val

    def get_template_names(self):
        #log.debug("get_template_names ()|%s %s %s", self.request.method, self.request.path, self.template_name)
        val = ['']
        if self.template_name:
            val = super(AccessAccountControlSubscription, self).get_template_names()
        #log.debug("get_template_names return: %s", val)
        return val

    def get(self, request, *args, **kwargs):
        #log.debug("get (%s, %s) -> %s -- self_U: %s -- req_U: %s", args, kwargs, self.request.path, self.request.user, request.user)
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
        val = super(AccessAccountControlSubscription, self).get(request, *args, **kwargs)
        #log.debug("get return: %s", val)
        ##log.debug("get REQ: %s", self.request)
        return val

    def post(self, request, *args, **kwargs):
        if kwargs.has_key('action'):
            #log.error("ACTION KEY IN POST = %s", kwargs.get('action'))
            if kwargs.get('action') == 'signup': self.signup = True
            if kwargs.get('action') == 'chpsw': self.chpsw = True
            if kwargs.get('action') == 'chprofile': self.chprofile = True
            if kwargs.get('action') == 'forgotpsw': self.forgotpsw = True
            if kwargs.get('action') == 'resetpsw': self.resetpsw = True
        #log.debug("post [req: %s] (%s, %s) -- SELF path: %s", request, args, kwargs, self.request.path)
        val = super(AccessAccountControlSubscription, self).post(request, *args, **kwargs)
        #log.debug("post form is valid: %s", getattr(self, 'form_is_valid', False))
        if getattr(self, 'form_is_valid', False):
            if self.resetpsw:
                #log.error("IN RESETPSW")
                #log.error("ID %s", self.iduser)
                try:
                    self.iduser = request.GET['id']
                    reset_psw = ResettablePassword.objects.get(session=self.iduser)
                    date_limit = datetime.now() - timedelta(days=2)
                    if reset_psw.date < date_limit:
                        #log.error("troppo vecchia, da eliminare")
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
                    #log.error("Exc in RESETPSW %s", e)
                    return HttpResponseRedirect(".?id=%s&error=True" % self.iduser)
            if self.forgotpsw:
                #log.error("IN FORGOTPSW %s", self.request.POST['username'])
                try:
                    #log.error("usermail %s", self.request.POST['username'])
                    user = User.objects.get(username=self.request.POST['username'])
                    self._notify_user_via_mail_forgotpsw(user, request.session)
                except Exception, e:
                    log.error("Exc in forgotpsw for name %s, %s", self.request.POST['username'], e)
                    pass
                return val
            if self.chprofile:
                user = request.user
                #log.error("IN CHPROFILE %s", user)
                try:
                    access_user = AccessAccount.objects.filter(user=user)[0]
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
                    log.debug('Exception occurred during changing profile: %s', e)
                    return val
            if self.chpsw:
                user = request.user
                #log.debug("IN CHPSW %s", user)
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
                    log.debug('Exception occurred during changing psw: %s', e)
                    return val
            if self.signup:
                try:
                    usernew = AccessAccount()
                    user = User()
                    #log.debug("USER-CREATING - %s", self.request.POST['email'])
                    user.email = self.request.POST['email']
                    user.username = self.request.POST['nickname']
                    user.first_name = self.request.POST['first_name']
                    user.last_name = self.request.POST['last_name']
		    user.is_active = True
                    usernew.phone = self.request.POST['phone']
                    usernew.mobile_phone = self.request.POST['phone_mobile']
                    usernew.company = self.request.POST['company']
                    usernew.partita_iva = self.request.POST['partita_iva']
                    usernew.address = self.request.POST['address']
                    usernew.cap = self.request.POST['cap']
                    usernew.location = self.request.POST['location']
                    usernew.paese = self.request.POST['paese']
                    user.set_password(self.request.POST['password'])
		    user.save()
                    usernew.user = user
		    usernew.save()
                    #log.debug("USER-CREATED - %s", self.request.POST['nickname'])
                    user = authenticate(username=self.request.POST['nickname'],
                                    password=self.request.POST['password'])
	            login(self.request, user)
                except Exception, e:
                    log.debug("Exception occurred during creation of USER %s -- %s", self.request.POST['nickname'], e)
                    return val 
                var = 'signup'
                #self._notify_user_via_mail(usernew, var)
                #self._notify_admin_via_mail_for_new_user(usernew, var)
                return val
            try:
                user = authenticate(username=self.request.POST['username'],
                                    password=self.request.POST['password'])
                #log.debug("authenticate return: %s", user)
                if user is not None:
                    if user.is_active:
                        #log.debug("You provided a correct username and password!")
                        login(self.request, user)
                        #log.debug("Login ret: %s", self.request.user)
                        var = 'login'
                        #self._notify_user_via_mail(self.request.user, var)
                        try:
                            AccessAccount.objects.get(user=user)
                            log.error("%s Existing AccessAccount",user)
                        except Exception, e:
                            #log.error("Not existing %s AccessAccount: %s", user, e)
                            try:
                                new = AccessAccount()
                                new.user = user
                                new.save()
                            except Exception, e:
                                log.error("Problems in creating %s AccessAccount from auth in auto: %s", user, e)
                        if not request.user.email:
			    #log.error("Utente creato in auto, non ha l'email: ragionare a fondo su come mandarlo per forza a modificare le sue credenziali la prima volta")
                            return HttpResponseRedirect('/access/chprofile/?newuser=True')
                        else:
                            redirect_to = request.REQUEST.get('next', '')
                            if not redirect_to:
                                redirect_to = "/"
                            #log.error("REDIREZIONE A: %s", redirect_to)
                            return HttpResponseRedirect(redirect_to)
                    else:
                        log.debug("Your account has been disabled!")
                else:
                    log.debug("Your username and password were incorrect.")
            except Exception, e:
                log.error("Auth Error: %s", e)
        else: # INVALID, to still here
            return super(AccessAccountControlSubscription, self).get(request, *args, **kwargs)
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
            log.error("Exc in send mail, no email?? %s", e)
            mailto = None
	kwargs = {'type':'forgotpsw','mailto':[mailto], 'type_dict':'single', mailto : {'user': nice_name(user), 'link' : Site.objects.get_current().domain +"/access/resetpsw/?id="+ session.session_key + user.username }}
        return SendTypeMail(kwargs)

@login_required
def profile(request):
    try:
        account = AccessAccount.objects.get(user=request.user)
    except Exception, e:
        log.error(e)
    try:
        changed = request.GET['changed']
    except:
        pass
    return render_to_response('access_account/profile.html', locals(), RequestContext(request))

