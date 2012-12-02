# pylint: disable-msg=C0103,W0212
# -*- coding: utf-8  -*-
# vim: set fileencoding=utf-8 :
# django.contrib.aderit.access_account -- python module for auth management
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
'''Built-in, globally-available admin actions.'''

from django.contrib import admin
from django import template
from django.contrib.admin import helpers
from django.contrib.admin.util import model_ngettext
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.log import getLogger
from django.http import HttpResponse
import csv

logger = getLogger('aderit.generic_utils.actions')


def export_as_csv_action(modeladmin, request, queryset):
    """
    Exports all selected objects from model
    """
    opts = modeladmin.model._meta
    fields = [field.name for field in opts.fields]
    app_label = opts.app_label
    if request.POST.get('post'):
        fields_wanted = []
        for i in request.POST.items():
            if str(i[0]).startswith('field-'):
                fields_wanted.append(str(i[0])[6:])
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % \
            unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        writer.writerow(list(fields_wanted))

        n = queryset.count()
        if n:
            for obj in queryset:
                writer.writerow([unicode(getattr(obj, field))
                                 .encode("utf-8", "replace")
                                 for field in fields_wanted])
        _msg_fmt = _("Successfully exported %(count)d %(items)s.")
        _msg = _msg_fmt % {"count": n,
                           "items": model_ngettext(modeladmin.opts, n)}
        modeladmin.message_user(request, _msg)
        return response

    context = {
        "title": _("What do you want export?"),
        "object_name": force_unicode(opts.verbose_name),
        "queryset": queryset,
        "exportable_objects": fields,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    req_context = template.RequestContext(request)
    return render_to_response("admin/export_as_csv_action.html",
                              context, context_instance=req_context)


admin.site.add_action(export_as_csv_action, 'export_as_csv_action')
export_as_csv_action.short_description = \
    _("Export as CSV all selected elements")
