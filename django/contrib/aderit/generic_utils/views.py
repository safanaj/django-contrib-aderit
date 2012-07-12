from django.http import HttpResponsePermanentRedirect

def external_view(request, target):
    return HttpResponsePermanentRedirect('http://' + target)

## USAGE
## (comodo per django cms nelle impostazioni avanzate, il redirect ad una pagina)
## in urls.py 
## from django.contrib.aderit.generic_utils.views import external_view

## urlpatterns = (
## url(r'^offsite/(?P<target>.+)$', external_view),
## )

