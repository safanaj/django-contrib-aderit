from datetime import datetime, timedelta, date
from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.sites.models import Site
import logging, re

register = template.Library()

"""
Usage:

{% get_my_current_site CS %}
{{CS.name|upper}}

e anche

{% get_sites sites %}
{% for site in sites %}
{{site.name}}
{% endfor %}

"""

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
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
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
    "Return a SitesNode"
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    #print "Tag: %s -- Var: %s" % (tag_name, var_name)
    return CurrentSiteNode(var_name)



