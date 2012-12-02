# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# pylint: disable-msg=W0232,R0903

# models.py -- send_mail.models
#
# Copyright (C) 2012 Aderit srl
#
# Authors: Matteo Atti <matteo.atti@aderit.it>, <attuch@gmail.com>
#          Marco Bardelli <marco.bardelli@aderit.it>,
#                         <bardelli.marco@gmail.com>
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

'''Sending mails models.'''

from django.db import models
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
    type_mail = models.CharField(max_length=125, unique=True,
                                 help_text=_('Scegli tipologia di mail,'
                                             ' deve corrispondere'
                                             ' alla chiave "type" inviata '
                                             'nelle kwargs'))
    body_txt = models.TextField(max_length=125, blank=True, null=True,
                                help_text=_('Il corpo della mail, in formato'
                                            ' testuale. '
                                            '<br/>Si possono utilizzare chiavi'
                                            ' che corrispondano alle chiavi '
                                            'delle kwargs formattate'
                                            ' in questo modo: '
                                            '{{ user }}, {{ password }} ...'))
    body_html = models.TextField(max_length=125, blank=True, null=True,
                                 help_text=_('Il corpo della mail, consente '
                                             'di usare markup html. '
                                             '<br/>Si possono utilizzare '
                                             'chiavi che corrispondano alle '
                                             'chiavi delle kwargs '
                                             'formattate in questo modo: '
                                             '{{ user }}, {{ password }} ...'))
    subject = models.CharField(max_length=125,
                               help_text=_("L'oggetto della mail"))
    mail_sender = models.CharField(max_length=125,
                                   help_text=_("Colui che invia la mail"
                                               " (es. info@...)"))
    attachments = models.ManyToManyField(Attach, blank=True, null=True,
                                         help_text=_("Allegati della "
                                                     "mail<br/>"))

    class Meta:
        verbose_name = _('Send Mail')
        verbose_name_plural = _('Send Mails')
        ordering = ["type_mail"]

    def __unicode__(self):
        return self.type_mail
