from django.conf.urls.defaults import *
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.decorators import login_required
from account.views import (AccountUpdateView, AccountSignupView,
                           AccountLoginView, AccountLogoutView)

from account.models import Account

#TODO nominare tutti gli urls e dargli un nome per il reverse; renderli anche piu' chiari

urlpatterns = patterns('',
    url(r'^login$',
        AccountLoginView.as_view(redirect_to='/'),
        name='login'),

    url(r'^login2$',
        AccountLoginView.as_view(redirect_to='/', use_captcha=True),
        name='login'),

    url(r'^logout$',
        AccountLogoutView.as_view(redirect_to='/'),
        name='logout'),

    url(r'^signup_mine$',
        AccountSignupView.as_view(model=Account),
        name='signup-mine'),


    url(r'^chprofile(/(?P<slug>.*))?$',
        login_required(AccountUpdateView.as_view(model=Account, slug_field='id', use_captcha=True,
                                                 template_name="account/chprofile.html",
                                                 success_url="/")),
        name='chprofile'),

    url(r'^viewprofile/(?P<slug>\d+)/$',
        login_required(DetailView.as_view(model=Account,
                                          template_name="account/profile.html",
                                          slug_field="id",
                                          context_object_name="account")),
        name='viewprofile'),


    url(r'^signup$', CreateView.as_view(model=Account,
                                        template_name="registration/signup_as_p.html"),
        name='signup'),

)

