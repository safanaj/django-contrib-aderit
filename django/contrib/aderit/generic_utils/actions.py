"""
Built-in, globally-available admin actions.
"""

from django.contrib import admin
from django import template
from django.core.exceptions import PermissionDenied
from django.contrib.admin import helpers
from django.contrib.admin.util import get_deleted_objects, model_ngettext
from django.db import router
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy, ugettext as _
from django.http import HttpResponse
import csv, logging

logger = logging.getLogger('django.debug')

def export_as_csv_action(modeladmin, request, queryset):
    """
    Exports all selected objects from model
    """
    opts = modeladmin.model._meta
    fields = [field.name for field in opts.fields]
    app_label = opts.app_label
    header=True
    if request.POST.get('post'):
        fields_wanted = []
        for i in request.POST.items():
            if str(i[0]).startswith('field-'):
                fields_wanted.append(str(i[0])[6:])
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
        writer = csv.writer(response)
        writer.writerow(list(fields_wanted))

        n = queryset.count()
        if n:
            for obj in queryset:
                writer.writerow([unicode(getattr(obj, field)).encode("utf-8","replace") for field in fields_wanted])
        modeladmin.message_user(request, _("Successfully exported %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
                })
        return response

    context = {
        "title": _("What do you want export?"),
        "object_name": force_unicode(opts.verbose_name),
        "queryset": queryset,
        "exportable_objects": fields,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    return render_to_response("admin/export_as_csv_action.html", context, context_instance=template.RequestContext(request))


admin.site.add_action(export_as_csv_action, 'export_as_csv_action')
export_as_csv_action.short_description = ugettext_lazy("Export as CSV all selected elements")
