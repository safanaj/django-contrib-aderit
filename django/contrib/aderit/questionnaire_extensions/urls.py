from django.conf.urls.defaults import url, patterns
from django.contrib.aderit.questionnaire_extensions.views import (ShowReport,
                                                                  ExportCsv,
                                                                  SendInvitation)
from django.utils.log import getLogger

logger = getLogger('aderit.questionnaire_extensions.urls')

urlpatterns = patterns('',                  
                       url(r'^showreport/(?P<slug>.*)/$',
                           ShowReport.as_view(template_name="questionnaire/report.html",
                                              slug_field="id"),
                           name='show_report'),
                       url(r'^csvexport/(?P<slug>\d+)/$',
                           ExportCsv.as_view(slug_field="id"),
                           name='exportcsv'),
                       url(r'^csvsubjexport/(?P<slug>\d+)/(?P<subjid>\d+)/$',
                           ExportCsv.as_view(slug_field="id"),
                           name='exportsubjcsv'),
                       url(r'^send/(?P<slug>\d+)/$',
                           SendInvitation.as_view(slug_field="id"),
                           name='sendinvitation'),
                       )
