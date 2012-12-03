# -*- coding: utf-8  -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=C0103

# nice_name.py -- templatetag for nice_name
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

'''Template tag for a nice name (full name) of user.'''

from django import template
register = template.Library()


@register.filter
def nice_name(user):
    """
    Example::
        {% load nice_name %}
        Hi, {{ user|nice_name }}
    """
    return user.get_full_name() or user.username
