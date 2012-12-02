# -*- coding: utf-8  -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=C0103,E1101,W0142,W0105,W0702,W0612,W0613

# currentsitetags.py -- templatetag for current site
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

'''Template tag for current site.'''

from django import template
from django.contrib.sites.models import Site

register = template.Library()


class SitesNode(template.Node):
    "TemplateNode for Sites"
    def __init__(self, var_name):
        self.varname = var_name

    def render(self, context):
        try:
            sites = Site.objects.order_by('id')
        except:
            sites = None
        context[self.varname] = sites
        return ''


@register.tag
def get_sites(parser, token):
    "Return a SitesNode"
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires"\
            " a single argument" % token.contents.split()[0]
    return SitesNode(var_name)


class CurrentSiteNode(template.Node):
    "TemplateNode for Current Site"
    def __init__(self, var_name):
        self.varname = var_name

    def render(self, context):
        try:
            current_site = Site.objects.get_current()
        except:
            current_site = None
        context[self.varname] = current_site
        return ''


@register.tag
def get_my_current_site(parser, token):
    """Return a SitesNode

    Usage:

    {% get_my_current_site CS %}
    {{CS.name|upper}}

    e anche

    {% get_sites sites %}
    {% for site in sites %}
    {{site.name}}
    {% endfor %}
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires"\
            " a single argument" % token.contents.split()[0]
    #print "Tag: %s -- Var: %s" % (tag_name, var_name)
    return CurrentSiteNode(var_name)
