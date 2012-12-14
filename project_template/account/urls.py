from django.conf.urls.defaults import url, patterns

from django.contrib.aderit.access_account.views import (LoginView, LogoutView,
                                                        UpdateView,
                                                        ChangePasswordView,
                                                        ForgotPasswordView,
                                                        DetailView)

from account.models import Account

from account.utils import callback_on_login, callback_on_signup

from account.views import SignupView

urlpatterns = patterns('',
    (r'^$', LoginView.as_view(redirect_to='/', allow_token=True,
                              template_name="account/account_form_as_ul.html")),

    url(r'^login/((?P<token>.+)/)?$',
        LoginView.as_view(allow_token=True,
                          after_login_callback=callback_on_login,
                          debug_dispatch_method=False,
                          template_name="account/account_form_as_ul.html",
                          delete_token_after_use=True),
        name='login'),

    url(r'^logout/$',
        LogoutView.as_view(redirect_to='/', clean_response_cookies=True, debug_dispatch_method=False),
        name='logout'),

    url(r'^signup/$',
        SignupView.as_view(model=Account, use_captcha=True,
                           additional_exclude_formfields=['token'],
                           require_formfields=['email'],
                           after_signup_callback=callback_on_signup,
                           debug_dispatch_method=True, debug_dispatch_method_full=False,
                           template_name="account/account_form_as_ul.html"),
        name='signup'),


    url(r'^password/change/((?P<slug>\d+)/)?$',
        ChangePasswordView.as_view(model=Account, use_login_required_decorator=True,
                                   template_name="account/account_form_as_ul.html",
                                   change_done_template_name="account/pswchanged.html",
                                   slug_field="id"),
        name='chpsw'),

    url(r'^password/forgot/((?P<token>.+)/)?$',
        ForgotPasswordView.as_view(template_name="account/account_form_as_ul.html",
                                   success_template_name="account/forgot_psw_ok.html",
                                   change_password_named_url='chpsw'),
        name='forgotpsw'),


    url(r'^chprofile/(?P<slug>.*)/$',
        UpdateView.as_view(model=Account, slug_field='id', additional_exclude_formfields=['token'],
                           use_captcha=False, use_login_required_decorator=True,
                           template_name="account/account_form_as_ul.html",
                           success_url="/"),
        name='chprofile'),

    url(r'^profile/((?P<slug>\d+)/?)?$',
        DetailView.as_view(model=Account, use_login_required_decorator=True,
                           template_name="account/profile.html",
                           slug_field="id",
                           context_object_name="account"),
        name='profile'),
)
