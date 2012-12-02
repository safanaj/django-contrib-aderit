# -*- coding: utf-8  -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=C0103,W0142

# order_by.py -- templatetag for order_by
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

'''Template tag to order queryset.'''

from django.template import Library

register = Library()


@register.filter_function
def order_by(queryset, args):
    '''
    {% load order_by %}
    {% for item in your_list|order_by:"f1,-f2,other_class__field_name" %}
    '''
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)
