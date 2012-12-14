# pylint: disable-msg=C0301,C0103,W0201,W0212,E1101,E0611
# pep8: ignore=E201
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# views.py -- python module for auth management
#
# Copyright (C) 2012 Aderit srl
#
# Author: Marco Bardelli <marco.bardelli@aderit.it>, <bardelli.marco@gmail.com>
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
'''Authentication and user profile forms'''

from django.forms import fields
from django.utils.log import getLogger
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

logger = getLogger('aderit.access_account.forms')


class UserCreationEmailUniqueForm(UserCreationForm):
    """
    Form for user creation to ensure uniqueness of email.
    """
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
    }

    email = fields.EmailField(label=_("E-mail address"), required=True)

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_email(self):
        """
        Ensure that email is not yet used.
        """
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise ValidationError(self.error_messages['duplicate_email'])
