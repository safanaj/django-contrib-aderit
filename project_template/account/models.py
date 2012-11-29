# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
import re
from django.db import models
from django.db.models import fields as models_fields
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.log import getLogger
from django.utils.translation import ugettext_lazy as _

from django.contrib.aderit.access_account.models import AccessAccount

logger = getLogger('account.models')

phone_regex = r'^\+?[0-9]{3}[0-9 ]{5,18}$'

### User Profile Model
class Account(AccessAccount):
    phone = models_fields.CharField(_("Phone"), validators=[RegexValidator(regex=re.compile(phone_regex))], max_length=125, blank=True) # telefono fisso
    mobile_phone = models_fields.CharField(_("Mobile Phone"), validators=[RegexValidator(regex=re.compile(phone_regex))], max_length=125, blank=True) # telefono mobile
    company = models_fields.CharField(_("Company"), max_length=125, blank=True) # ragione sociale
    address = models_fields.CharField(_("Address"), max_length=125, blank=True) # indirizzo di fatturazione
    zip_code = models_fields.CharField(_("Zip Code"), max_length=125, blank=True) # cap
    location = models_fields.CharField(_("Location"), max_length=125, blank=True) # localita'
    country = models_fields.CharField(_("Country"), max_length=125, blank=True) # paese
    reported_by = models_fields.CharField(_("Reported By"), max_length=250, blank=True) # da chi ne ha sentito parlare

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        ordering = ["user"]

    def __unicode__(self):
        return self.user.username
