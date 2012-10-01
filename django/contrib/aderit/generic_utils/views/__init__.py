from django.http import HttpResponsePermanentRedirect
from django.views.generic import View
def external_view(request, target):
    return HttpResponsePermanentRedirect('http://' + target)

## USAGE
## (comodo per django cms nelle impostazioni avanzate, il redirect ad una pagina)
## in urls.py
## from django.contrib.aderit.generic_utils.views import external_view

## urlpatterns = (
## url(r'^offsite/(?P<target>.+)$', external_view),
## )

from autologin import AutoLoginView

class GenericUtilView(View):

    force_setup_attrs = False

    def _setup_attrs(self, **kwargs):
        for k in kwargs.keys():
            if self.force_setup_attrs or hasattr(self, k):
                setattr(self, k, kwargs.get(k))

    def dispatch(self, request, *args, **kwargs):
        self._setup_attrs(**kwargs)
        return super(GenericUtilView, self).dispatch(request, *args, **kwargs)
