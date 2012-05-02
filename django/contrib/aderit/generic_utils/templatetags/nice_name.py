from django import template

@register.filter
def nice_name(user):
    """
    Example::
    	{% load nice_name %}
        Hi, {{ user|nice_name }}
    """
    return user.get_full_name() or user.username
