#from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.defaults import *
from django.views.generic import TemplateView, ListView, DetailView
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Alternatively served by Web Server
    url(r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve',
        {'show_indexes':True, 'document_root': settings.STATIC_ROOT}),
    url(r'^media/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve',
        {'show_indexes':True, 'document_root': settings.MEDIA_ROOT}),
    url(r'^robots.txt/', TemplateView.as_view(template_name='robots.txt')),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
)
