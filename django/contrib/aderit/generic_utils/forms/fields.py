# pylint
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# django.contrib.aderit.generic_utils.forms -- generic formclass factory
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
'''Generic additional form fields (extensions to django.forms.fields)'''

from django.utils.translation import ugettext_lazy as _

from django.forms.fields import RegexField

PHONE_REGEX = r'^\+?[0-9]{3}[0-9 ]{5,18}$'


class GenericPhoneField(RegexField):
    '''
    Form field to manage/validate phone number.
    '''
    default_error_messages = {
        'invalid': _("Enter a valid phone number.")
    }

    def __init__(self, regex=PHONE_REGEX, max_length=None, min_length=None,
                 error_message=None, *args, **kwargs):
        super(GenericPhoneField, self).__init__(regex, max_length=max_length,
                                                min_length=min_length,
                                                error_message=error_message,
                                                *args, **kwargs)
