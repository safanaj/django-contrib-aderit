# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_init, post_save, pre_save
from django.core.mail import EmailMessage
from django.contrib.aderit.access_account.models import AccessAccount
import logging

class ResettablePassword(models.Model):
    user = models.ForeignKey(User)
    session = models.CharField(max_length=250)
    date = models.DateTimeField()

    class Meta:
        verbose_name = 'Resettable Password'
        verbose_name_plural = 'Resettable Password'
        ordering = ["user"]


class Account(AccessAccount):
    phone = models.CharField(max_length=125, blank=True) # telefono fisso
    mobile_phone = models.CharField(max_length=125, blank=True) # telefono mobile
    company = models.CharField(max_length=125, blank=True) # ragione sociale
    address = models.CharField(max_length=125, blank=True) # indirizzo di fatturazione
    cap = models.CharField(max_length=125, blank=True) # cap
    location = models.CharField(max_length=125, blank=True) # localita'
    paese = models.CharField(max_length=125, blank=True) # paese

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ["user"]

    def __unicode__(self):
        return self.user.username

