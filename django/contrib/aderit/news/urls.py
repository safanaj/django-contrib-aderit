from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import ListView, DetailView
from django.contrib.aderit.news.models import *

PAGINATION = getattr(settings,'NEWS_PAGINATED_BY', 5)

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=NewsItem, template_name="news/news_list.html", paginate_by=PAGINATION, context_object_name='news_list'), name="news_list"),
    url(r'^detail/(?P<slug>\d+)/$', DetailView.as_view(model=NewsItem, template_name="news/news_detail.html", slug_field="id", context_object_name="news_detail"), name="news_detail"),

)
