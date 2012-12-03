# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# django.contrib.aderit.generic_utils.models -- django models extensions
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
'''Generic model fields'''

from django.utils.translation import ugettext_lazy as _

from django.db.models.fields import CharField
from django.contrib.aderit.generic_utils.forms import fields as forms_fields


class GenericPhoneField(CharField):
    description = _("Phone number")

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms_fields.GenericPhoneField
        }
        defaults.update(kwargs)
        return super(GenericPhoneField, self).formfield(**defaults)
