# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
from django.conf import settings
from django.http import HttpResponseRedirect
from django.forms import ModelForm, Form, fields as forms_fields
from django.contrib.auth.models import User
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm, PasswordChangeForm)
from django.contrib.aderit.generic_utils.currentUserMiddleware import get_current_user
from django.contrib.aderit.generic_utils.templatetags.nice_name import nice_name
from account.models import Account, ResettablePassword

import logging
import os, re, time

logger = logging.getLogger('django.debug')
logger.addHandler(logging.StreamHandler())
logger.handlers[0].setFormatter(logging.Formatter("%(name)s:%(levelname)s: %(message)s"))
logger.setLevel(logging.DEBUG)

if 'captcha' in settings.INSTALLED_APPS:
    from captcha.fields import CaptchaField

    class CaptchaForm(Form):
        captcha = CaptchaField(label="*Inserire Captcha", help_text = "(obbligatorio la per sicurezza)")


def is_only_numbers(stringa):
    if re.match("^[0-9]+$",stringa): return True
    else: return False

class ForgotPswUsernameForm(Form):
    username = forms_fields.RegexField(label="Username", max_length=125, regex=r'^[\w\s]+', required=True,
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
    nickname = forms_fields.RegexField(label="*Username", max_length=125, regex=r'^[\w\s]+',
                                help_text = "(da usare come username per il login)",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    first_name = forms_fields.RegexField(label="*Nome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    last_name = forms_fields.RegexField(label="*Cognome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    email = forms_fields.EmailField(label="*Email", help_text = "(inserire la mail di lavoro)", max_length=125)
    phone = forms_fields.CharField(label="Telefono Fisso",  required=False,
                                help_text = "(il numero telefonico dell'ufficio, non usare punteggiatura)")
    phone_mobile = forms_fields.CharField(label="Telefono Mobile", required=False,
                                help_text = "(il numero cellulare, non usare punteggiatura)")
    company = forms_fields.CharField(label="Ragione Sociale", max_length=125, required=False,
                                help_text = "(il nome dell'azienda per cui lavora)")
    address = forms_fields.CharField(label="Indirizzo", max_length=125, required=False,
                                help_text = "(indirizzo di fatturazione)")
    cap = forms_fields.CharField(label="CAP", required=False,
                                help_text = "(il cap associato all'indirizzo)")
    location = forms_fields.CharField(label="Localita'", max_length=125, required=False,
                                help_text = "(la localita' presso cui si lavora)")
    paese = forms_fields.CharField(label="Paese", max_length=125, required=False,
                                help_text = "(il paese presso cui si lavora)")

    def clean(self):
        cleaned_data = self.cleaned_data
        company = cleaned_data.get("company")
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
    nickname = forms_fields.RegexField(label="*Username", max_length=125, regex=r'^[\w\s]+',
                                help_text = "(da usare come username per il login)",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    first_name = forms_fields.RegexField(label="*Nome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    last_name = forms_fields.RegexField(label="*Cognome", max_length=125, regex=r'^[\w\s]+',
                                help_text = "<br/>",
                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    email = forms_fields.EmailField(label="*Email", help_text = "(inserire la mail di lavoro)", max_length=125)
    phone = forms_fields.CharField(label="Telefono Fisso", required=False,
                                help_text = "(il numero telefonico dell'ufficio, non usare punteggiatura)")
    phone_mobile = forms_fields.CharField(label="Telefono Mobile", required=False,
                                help_text = "(il numero cellulare, non usare punteggiatura)")
    password = forms_fields.CharField(label="*Password", widget=forms_fields.PasswordInput, max_length=30,
                                help_text = "(usare una password sicura, contenente numeri e lettere)")
    password_confirm = forms_fields.CharField(label="*Password confirmation", widget=forms_fields.PasswordInput, max_length=30,
                                help_text = "(inserire la stessa password per verifica)")
    company = forms_fields.CharField(label="Ragione Sociale", max_length=125, required=False,
                                help_text = "(il nome dell'azienda per cui lavora)")
    address = forms_fields.CharField(label="Indirizzo", max_length=125, required=False,
                                help_text = "(indirizzo di fatturazione)")
    cap = forms_fields.CharField(label="CAP", required=False,
                                help_text = "(il cap associato all'indirizzo)")
    location = forms_fields.CharField(label="Localita'", max_length=125, required=False,
                                help_text = "(la localita' presso cui si lavora)")
    paese = forms_fields.CharField(label="Paese", max_length=125, required=False,
                                help_text = "(il paese presso cui si lavora)")

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
    password_new = forms_fields.CharField(label="*Nuova Password", widget=forms_fields.PasswordInput, max_length=30,
                                help_text = "(inserire la nuova password)")
    password_new_confirm = forms_fields.CharField(label="*Conferma nuova Password", widget=forms_fields.PasswordInput, max_length=30,
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
    password_old = forms_fields.CharField(label="*Vecchia Password", widget=forms_fields.PasswordInput, 
                                help_text = "(inserire la vecchia password)",
                                error_messages = {'invalid': "Password errata"})
    password_new = forms_fields.CharField(label="*Nuova Password", widget=forms_fields.PasswordInput, max_length=30,
                                help_text = "(inserire la nuova password)")
    password_new_confirm = forms_fields.CharField(label="*Conferma nuova Password", widget=forms_fields.PasswordInput, max_length=30,
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
