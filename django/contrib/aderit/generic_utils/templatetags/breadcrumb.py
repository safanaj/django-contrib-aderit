import django
from django import template
from django.core.urlresolvers import resolve
from django.template.defaulttags import url
from django.template import Node, TemplateSyntaxError
from treemenus.models import Menu, MenuItem
from treemenus.config import APP_LABEL
import logging

logger = logging.getLogger("django.debug")

register = template.Library()

def breadcrumb_for(m):
    bread = [m]
    if m.parent_id and m.parent.parent_id: bread.extend(breadcrumb_for(m.parent))
    return bread

def show_breadcrumb(context, menu_name):
    request = context['request']
    current_url = resolve(request.get_full_path()).url_name
    try:
        current = MenuItem.objects.get(menu__name=menu_name, named_url=current_url)
        context['breadcrumb'] = breadcrumb_for(current)
        context['breadcrumb'].reverse()
    except:
	pass
    return context

register.inclusion_tag('%s/breadcrumb.html' % APP_LABEL, takes_context=True)(show_breadcrumb)


#EXAMPLE USAGE

"""
=======
#INSTALLED_APPS (settings.py)

...
  'treemenus',
  'django.contrib.aderit.generic_utils',
...

#TEMPLATE PARENT (base.html)

...
{% show_breadcrumb "MyMenu" %}
...

#TEMPLATE treemenus/breadcrumb.html

{% load i18n breadcrumb tree_menu_tags %}

{% for i in breadcrumb %}
   {% if i == breadcrumb|last %}
     <span>{{i.caption}}</span>
   {% else %}
     <a href="{% reverse_named_url i.named_url %}">{{i.caption}}</a>&nbsp; &gt; 
   {% endif %}
{% endfor %}

"""
