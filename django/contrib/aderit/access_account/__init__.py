from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable
from django.utils.translation import ugettext as _
from django.utils.importlib import import_module

def _get_model_from_auth_profile_module():
    """
    Get model for UserProfile.

    The call 'request.user.get_profile()' can raise two types of Exceptions:
       - AttributeError if request.user is anonymous.
       - <UserProfileModel>.DoesNotExist if UserProfile have to be create yet.
    """
    if not hasattr(settings, 'AUTH_PROFILE_MODULE'):
        exc_txt = "To use AccessAccount, you need to subclass AccessAccount"
        exc_txt += " abstract Model and define AUTH_PROFILE_MODULE coerently."
        raise SiteProfileNotAvailable(_(exc_txt))
    module_name = "%s.models" % settings.AUTH_PROFILE_MODULE.split('.')[0]
    module = import_module(module_name)
    return getattr(module, settings.AUTH_PROFILE_MODULE.split('.')[1])
