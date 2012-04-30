# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
import logging

class Attach(models.Model):
    name = models.CharField(max_length=125)
    attachment = models.FileField(upload_to='send_mail_attach/')

    class Meta:
        verbose_name = 'Mail Attach'
        verbose_name_plural = 'Mail Attachments'

    def __unicode__(self):
        return self.name

types = (('text','text'),('html','html'))

class SendMail(models.Model):
    type_mail = models.CharField(max_length=125, help_text='Scegli tipologia di mail, deve corrispondere alla chiave "type" inviata nelle kwargs')
    body = models.TextField(max_length=125, help_text='Il corpo della mail, consente di usare markup html. <br/>Si possono utilizzare chiavi che corrispondano alle chiavi delle kwargs formattate in questo modo: {{ user }}, {{ password }} ...')
    subject = models.CharField(max_length=125, help_text="L'oggetto della mail")
    mail_sender = models.CharField(max_length=125, help_text="Colui che invia la mail (es. info@...)")
    attachments = models.ManyToManyField(Attach, blank=True, null=True, help_text="Allegati della mail<br/>")
    content_subtype = models.CharField(choices=types, max_length=125, default='text', help_text="Se nel body e' stato usato html, scegliere html per inviare in formato text/html")

    class Meta:
        verbose_name = 'Send Mail'
        verbose_name_plural = 'Send Mails'
        ordering = ["type_mail"]

    def __unicode__(self):
        return self.type_mail

