from django.db import models
from django.contrib import admin
#from django_extensions.admin import ForeignKeyAutocompleteAdmin
from django.contrib.aderit.generic_utils.export_as_csv_action import export_as_csv_action
from django.contrib.aderit.generic_utils.autologin.utils import gen_autologin_rand_code
from django.contrib.aderit.generic_utils.export_as_csv_action import export_as_csv_action
from account.models import *

#class AccountAdmin(ForeignKeyAutocompleteAdmin):
# class AccountAdmin(admin.ModelAdmin):
#     list_display = ['user', 'company']
#     related_search_fields = { 'user' : ('username','first_name','last_name','email') }
#     list_filter = ('user__username', 'company')
#     search_fields = ['user__username', 'company']
#     actions = [export_as_csv_action("CSV Export", fields=['user'])]

class ResettablePasswordAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'date']
    app_name = 'Auth'

#admin.site.register(Account, AccountAdmin)
admin.site.register(ResettablePassword, ResettablePasswordAdmin)


from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'account'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (AccountInline, )
    actions = [gen_autologin_rand_code,
               export_as_csv_action("CSV Export", exclude=['username', 'first_name'])]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
