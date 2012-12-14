# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
from django.conf import settings
from django.db.models import fields as models_fields
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.log import getLogger
from django.utils.translation import ugettext_lazy as _

from django.contrib.aderit.access_account.models import AccessAccount
from django.contrib.aderit.generic_utils.models.fields import \
    GenericPhoneField as PhoneField

logger = getLogger('account.models')


### User Profile Model
class Account(AccessAccount):
    phone = PhoneField(_("Phone"), max_length=125, blank=True)  # home phone
    mobile_phone = PhoneField(_("Mobile Phone"), max_length=125, blank=True)  # mobile phone
    reported_by = models_fields.CharField(_("Reported By"), max_length=250, blank=True)  # who spoke about

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        ordering = ["user"]

    def __unicode__(self):
        return self.user.username
