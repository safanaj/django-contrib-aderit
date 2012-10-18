from django.conf import settings
from django import template
from django.contrib.aderit.news.models import NewsItem
from datetime import datetime, timedelta, date

DURATION = getattr(settings,'NEWS_DURATION_VISIBILITY', 30)

register = template.Library()

class LatestNewsNode(template.Node):
    def __init__(self, varname, limit):
        self.limit = limit
        self.varname = varname

    def render(self, context):
        a = datetime.now() - timedelta(DURATION)
        news = NewsItem.objects.filter(pub_date__gt = a)[:self.limit]
        context[self.varname] = news
        return ''

@register.tag
def get_latest_news(parser, token):
    """
    {% get_latest_news 5 as news %}
    """
    bits = token.split_contents()
    if len(bits) == 3:
        limit = None
    elif len(bits) == 4:
        try:
            limit = abs(int(bits[1]))
        except ValueError:
            raise template.TemplateSyntaxError("If provided, second argument to `get_latest_news` must be a positive whole number.")
    if bits[-2].lower() != 'as':
        raise template.TemplateSyntaxError("Missing 'as' from 'get_latest_news' template tag. Format is {% get_latest_news 5 as news %}.")
    return LatestNewsNode(bits[-1], limit)

@register.inclusion_tag('%s' % getattr(settings, "NEWS_TEMPLATE_NAME", "news/news.html"), takes_context=True)
def show_latest_news(context, limit):
    """
    {% show_latest_news 5 %}
    """
    a = datetime.now() - timedelta(DURATION)
    context['news'] = NewsItem.objects.filter(pub_date__gt = a)[:limit]
    return context
