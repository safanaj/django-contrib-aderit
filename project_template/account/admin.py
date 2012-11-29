from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from account.models import Account

class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = _('accounts')

class UserAdmin(UserAdmin):
    inlines = (AccountInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
