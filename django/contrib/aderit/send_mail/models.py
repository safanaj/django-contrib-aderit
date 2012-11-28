# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.log import getLogger
from django.utils.translation import ugettext_lazy as _

class Attach(models.Model):
    name = models.CharField(max_length=125)
    attachment = models.FileField(upload_to='send_mail_attach/')

    class Meta:
        verbose_name = _('Mail Attach')
        verbose_name_plural = _('Mail Attachments')

    def __unicode__(self):
        return self.name

class SendMail(models.Model):
    type_mail = models.CharField(max_length=125,
                                 help_text=_('Scegli tipologia di mail, deve corrispondere'\
                                                 ' alla chiave "type" inviata nelle kwargs'), unique=True)
    body_txt = models.TextField(max_length=125,
                                help_text=_('Il corpo della mail, in formato testuale.'\
                                                ' <br/>Si possono utilizzare chiavi che '\
                                                'corrispondano alle chiavi delle kwargs '\
                                                'formattate in questo modo: {{ user }}, {{ password }} ...'),
                                blank=True, null=True)
    body_html = models.TextField(max_length=125,
                                 help_text=_('Il corpo della mail, consente di usare '\
                                                 'markup html. <br/>Si possono utilizzare '\
                                                 'chiavi che corrispondano alle chiavi delle kwargs '\
                                                 'formattate in questo modo: {{ user }}, {{ password }} ...'),
                                 blank=True, null=True)
    subject = models.CharField(max_length=125, help_text=_("L'oggetto della mail"))
    mail_sender = models.CharField(max_length=125, help_text=_("Colui che invia la mail (es. info@...)"))
    attachments = models.ManyToManyField(Attach, blank=True, null=True, help_text=_("Allegati della mail<br/>"))

    class Meta:
        verbose_name = _('Send Mail')
        verbose_name_plural = _('Send Mails')
        ordering = ["type_mail"]

    def __unicode__(self):
        return self.type_mail

