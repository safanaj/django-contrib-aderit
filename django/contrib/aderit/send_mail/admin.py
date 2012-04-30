from django.db import models
from django.contrib import admin
from models import *
from django.contrib.admin.widgets import AdminDateWidget

class SendMailAdmin(admin.ModelAdmin):
    list_display = ['id','type_mail', 'subject', 'mail_sender']
    list_editable = ('type_mail','subject','mail_sender')
    list_filter = ('type_mail', 'subject','mail_sender')
    search_fields = ['type_mail', 'subject','mail_sender']

admin.site.register(SendMail, SendMailAdmin)

