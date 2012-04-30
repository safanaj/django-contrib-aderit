# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
import logging

class SendMail(models.Model):
    type_mail = models.CharField(max_length=125)
    body = models.TextField(max_length=125)
    subject = models.CharField(max_length=125)
    mail_sender = models.CharField(max_length=125)

    class Meta:
        verbose_name = 'Send Mail'
        verbose_name_plural = 'Send Mails'
        ordering = ["type_mail"]

    def __unicode__(self):
        return self.type_mail

