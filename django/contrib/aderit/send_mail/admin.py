# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=R0904

# admin.py -- admin for send_mail.models
#
# Copyright (C) 2012 Aderit srl
#
# Author: Matteo Atti <matteo.atti@aderit.it>, <attuch@gmail.com>
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

'''Sending mails admin models.'''

from django.contrib import admin
from django.contrib.aderit.send_mail.models import SendMail, Attach


class AttachAdmin(admin.ModelAdmin):
    list_display = ['attachment']


class SendMailAdmin(admin.ModelAdmin):
    list_display = ['id', 'type_mail', 'subject', 'mail_sender']
    list_editable = ('type_mail', 'subject', 'mail_sender')
    list_filter = ('type_mail', 'subject', 'mail_sender')
    search_fields = ['type_mail', 'subject', 'mail_sender']

admin.site.register(SendMail, SendMailAdmin)
admin.site.register(Attach, AttachAdmin)
