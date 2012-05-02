from datetime import datetime, timedelta, date
from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User
from utilstag.middleware import get_current_user
import logging, re

"""
Usage:
{% get_user_groups groups %}
{{ groups }}
"""

register = template.Library()

class CurrentUserGroups(template.Node):
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
    "Return all groups of logged user"
    try:
        user_name = get_current_user()
        logging.error(user_name)
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]
    logging.error("Tag: %s -- Var: %s -- User: %s" % (tag_name, var_name, user_name))
    return CurrentUserGroups(var_name, user_name)

