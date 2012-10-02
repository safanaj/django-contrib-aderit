from django.db import models
from django.contrib import admin
from django.contrib.aderit.generic_utils.export_as_csv_action import export_as_csv_action
import logging

logger = logging.getLogger("aderit.generic_utils.autologin.admin")

class AutoLoginCodeModelAdmin(admin.ModelAdmin):
    list_display = ('user','first_name','last_name','email','code')
    list_filter = ('user__username',)
    search_fields = ['user__username',]
    actions = [export_as_csv_action("CSV Export", fields=['user','first_name','last_name','email','code'])]

admin.site.register(AutoLoginCodeModel, AutoLoginCodeModelAdmin)
