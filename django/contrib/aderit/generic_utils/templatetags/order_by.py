from django.template import Library

register = Library()

@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

{% load order_by %}

{% for item in your_list|order_by:"field1,-field2,other_class__field_name" %}
