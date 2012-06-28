# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_init, post_save, pre_save
from django.core.mail import EmailMessage
import logging

class ResettablePassword(models.Model):
    user = models.ForeignKey(User)
    session = models.CharField(max_length=250)
    date = models.DateTimeField()

class AccessAccount(models.Model):
    user = models.ForeignKey(User) # che contiene nickname, nome referente e email
    phone = models.CharField(max_length=125, blank=True) # telefono fisso
    mobile_phone = models.CharField(max_length=125, blank=True) # telefono mobile
    company = models.CharField(max_length=125, blank=True) # ragione sociale
    address = models.CharField(max_length=125, blank=True) # indirizzo di fatturazione
    cap = models.CharField(max_length=125, blank=True) # cap
    location = models.CharField(max_length=125, blank=True) # localita'
    paese = models.CharField(max_length=125, blank=True) # paese
    partita_iva = models.CharField(max_length=125, blank=True) # ...

    class Meta:
        verbose_name = 'Account for Access'
        verbose_name_plural = 'Accounts for Accesses '
        ordering = ["user"]
        
    def __unicode__(self):
        return self.user.username

