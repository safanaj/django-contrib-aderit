import django
from django import template
from django.core.urlresolvers import resolve, reverse, NoReverseMatch, Resolver404
from django.template.defaulttags import url
from django.template import Node, TemplateSyntaxError
from treemenus.models import Menu, MenuItem
from treemenus.config import APP_LABEL
import logging

logger = logging.getLogger("aderit.generic_utils.breadcrumb")

register = template.Library()

def breadcrumb_for(m):
    bread = [m]
    if m.parent_id and m.parent.parent_id: bread.extend(breadcrumb_for(m.parent))
    return bread

def show_breadcrumb(context, menu_name):
    request = context['request']
    use_reverse = True
    current_url = request.path
    try:
        current_url_name = resolve(current_url).url_name
    except Resolver404:
        return context

    try:
        reverse(current_url_name)
    except NoReverseMatch:
        use_reverse = False

    logger.debug("Menu name: %s - current_url: %s - current_url_name: %s - use_reverse: %s",
                 menu_name, current_url, current_url_name, use_reverse)

    menu_item_kw = {'menu__name' : menu_name}
    if use_reverse:
        menu_item_kw.update({'named_url' : current_url_name})
    else:
        menu_item_kw.update({'url' : current_url})

    try:
        current = MenuItem.objects.get(**menu_item_kw)
        context['breadcrumb'] = breadcrumb_for(current)
        context['breadcrumb'].reverse()
    except MenuItem.DoesNotExist:
        logger.debug("DoesNotExist: use_reverse: %s - kw: %s", use_reverse, menu_item_kw)
        context['breadcrumb'] = []
        if use_reverse:
            try:
                current = MenuItem.objects.get(menu__name=menu_name, url=current_url)
                context['breadcrumb'] = breadcrumb_for(current)
                context['breadcrumb'].reverse()
            except MenuItem.DoesNotExist:
                logger.warning("DoesNotExist: for url: %s", current_url)
                context['breadcrumb'] = []
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
