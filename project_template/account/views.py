from django.conf import settings
from django.contrib.aderit.access_account.views import \
    (SignupView as AccessAccountSignupView)
from django.contrib.aderit.generic_utils.views import \
    (GenericUtilView, GenericProtectedView)

from django.utils.translation import ugettext_lazy as _
from django.utils.log import getLogger
from django.template.response import TemplateResponse

from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView

from django.http import HttpResponseRedirect, HttpResponse, urlparse

from django.core.urlresolvers import reverse

from account.models import Account

logger = getLogger('account.views')


class SignupView(AccessAccountSignupView):

    def get_initial(self):
        _reported_by = self.request.GET.get('reported_by', "")
        if _reported_by:
            return {'reported_by': _reported_by}
        return {}
