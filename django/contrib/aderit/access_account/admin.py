from django.db import models
from django.contrib import admin
from django.contrib.aderit.access_account.models import AccessAccount, ResettablePassword
from django.contrib.admin.widgets import AdminDateWidget
from django.http import HttpResponse
from datetime import datetime, timedelta, date
from django_extensions.admin import ForeignKeyAutocompleteAdmin
import csv


def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([unicode(getattr(obj, field)).encode("utf-8","replace") for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv


class AccessAccountAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ['user', 'company']
    related_search_fields = { 'user' : ('username','first_name','last_name','email') }
    list_filter = ('user__username', 'company')
    search_fields = ['user__username', 'company']
    actions = [export_as_csv_action("CSV Export", fields=['user','password'])]

class ResettablePasswordAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'date']

admin.site.register(AccessAccount, AccessAccountAdmin)
admin.site.register(ResettablePassword, ResettablePasswordAdmin)

