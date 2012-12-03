# -*- coding: utf-8  -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=C0103,E1101,W0142,W0105,W0702,W0612,W0613

# currentusergroupstags.py -- templatetag for current user groups
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

'''Template tag for groups of current user'''

from django import template
from django.contrib.auth.models import User
from django.utils.log import getLogger
from django.contrib.aderit.generic_utils.middleware import get_current_user

logger = getLogger('aderit.generic_utils.templatetags.currentusergroups')

register = template.Library()


class CurrentUserGroups(template.Node):
    '''Template node for get_user_groups tag'''
    def __init__(self, var_name, user_name):
        self.varname = var_name
        self.username = user_name

    def render(self, context):
        try:
            groups = User.objects.get(username=self.username).groups.all()
        except:
            groups = None
        context[self.varname] = groups
        return ''


@register.tag
def get_user_groups(parser, token):
    """Return all groups of logged user

    Usage:
    {% get_user_groups groups %}
    {{ groups }}
    """
    try:
        user_name = get_current_user()
        logger.error(user_name)
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires"\
            " one argument" % token.contents.split()[0]
    logger.error("Tag: %s -- Var: %s -- User: %s",
                 tag_name, var_name, user_name)
    return CurrentUserGroups(var_name, user_name)
