# -*- coding: utf-8  -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=C0103,C0301

"""
namefile: usertags.py
You would need a template nest for every method, for example to online_users.
/templates/tag/online_users.html

        {% if users %}
        <ul>
        {% for user in users %}
            <li>{{user.username}}</li>
        {% endfor %}
        </ul>
        {% endif %}

to load

{% load usertags %}
{% online_users 5 %}
{% last_registers 5 %}
{% last_logins 5 %}

"""

from django import template
from django.contrib.auth.models import User
import datetime

register = template.Library()


@register.inclusion_tag('tags/online_users.html')
def online_users(num):
    """
    Show user that has been login an hour ago.
    """
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    sql_datetime = datetime.datetime.strftime(one_hour_ago,
                                              '%Y-%m-%d %H:%M:%S')
    user_qs = User.objects.filter(last_login__gt=sql_datetime,
                                  is_active__exact=1)
    users = user_qs.order_by('-last_login')[:num]
    return {'users': users}


@register.inclusion_tag('tags/last_registers.html')
def last_registers(num):
    """
    Show last registered users.
    """
    user_qs = User.objects.filter(is_active__exact=1)
    users = user_qs.order_by('-date_joined')[:num]
    return {'users': users}


@register.inclusion_tag('tags/last_logins.html')
def last_logins(num):
    """
    Show last logins ...
    """
    user_qs = User.objects.filter(is_active__exact=1)
    users = user_qs.order_by('-last_login')[:num]
    return {'users': users}
