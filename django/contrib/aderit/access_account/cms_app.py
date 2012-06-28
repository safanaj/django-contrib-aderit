from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
admin.autodiscover()

class AccessAccountApp(CMSApp):
    name = _("AccessAccount App") # give your app a name, this is required
    urls = ["django.contrib.aderit.access_account.urls"] # link your app to url configuration(s)

apphook_pool.register(AccessAccountApp) # register your app

