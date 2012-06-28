from django.conf.urls.defaults import *
from django.contrib.aderit.access_account.views import AccessAccountControlSubscription
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('',
    url(r'^$', AccessAccountControlSubscription.as_view(template_name="access_account/access_accountcontrol.html")),
    url(r'^profile/', 'django.contrib.aderit.access_account.views.profile', name='profile'),
    url(r'^signup_done/', AccessAccountControlSubscription.as_view(template_name="access_account/post_creation.html"), name="signup_done"),
    url(r'^chpsw_done/', AccessAccountControlSubscription.as_view(template_name="access_account/chpsw.html"), name="chpsw"),
    url(r'^chprofile_done/', AccessAccountControlSubscription.as_view(template_name="access_account/chprofile.html"), name="chprofile"),
    url(r'^forgotpsw_done/', AccessAccountControlSubscription.as_view(template_name="access_account/forgotpsw.html"), name="forgotpsw"),
    url(r'^resetpsw_done/', AccessAccountControlSubscription.as_view(template_name="access_account/forgotpswreset.html"), name="resetpsw"),
    url(r'^bilancio_done/', AccessAccountControlSubscription.as_view(template_name="access_account/bilancio.html"), name="bilancio"),
    url(r'^forgotpsw/', AccessAccountControlSubscription.as_view(template_name="access_account/access_accountcontrol.html", forgotpsw=True)),
    url(r'^resetpsw/', AccessAccountControlSubscription.as_view(template_name="access_account/access_accountcontrol.html", resetpsw=True)),
    url(r'^signup/', AccessAccountControlSubscription.as_view(template_name="access_account/access_accountcontrol.html", signup=True)),
    url(r'^(?P<action>\w+)/', login_required(AccessAccountControlSubscription.as_view(template_name="access_account/access_accountcontrol.html")), name='action'),
    
)

