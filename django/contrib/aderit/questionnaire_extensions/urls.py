# django.contrib.aderit.questionnaire_extensions.urls -- python module
#
# Copyright (C) 2012 Aderit srl
#
# Author: Matteo Atti <matteo.atti@aderit.it>, <attuch@gmail.com>
#
# This file is part of DjangoContribAderit.
#
# DjangoContribAderit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DjangoContribAderit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DjangoContribAderit.  If not, see <http://www.gnu.org/licenses/>.
'''
Django Contrib Aderit Questionnaire Extensions urls
'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''


from django.conf.urls.defaults import url, patterns
from django.contrib.aderit.questionnaire_extensions.views import (ShowReport,
                                                                  ExportCsv,
                                                                  SendInvitation,
                                                                  ShowGraph)
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
                       url(r'^showgraph/(?P<slug>\d+)/$',
                           ShowGraph.as_view(template_name="questionnaire/quest_graph.html",
                                             slug_field="id"),
                           name='showgraph'),
                       )
