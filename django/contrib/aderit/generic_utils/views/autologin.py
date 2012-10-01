from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.generic import View
from django.contrib import auth
from django.contrib.auth.models import User
import hashlib
import logging

logger = logging.getLogger("aderit.generic_utils.views.autologin")

ALLOW_SUPERUSER = getattr(settings, 'AUTOLOGIN_ALLOW_SUPERUSER', False)
ALLOW_STAFF = getattr(settings, 'AUTOLOGIN_ALLOW_STAFF', False)
HASH_FUNC_NAME = getattr(settings, 'AUTOLOGIN_HASH_FUNC_NAME', 'md5')
DEFAULT_REDIRECT_URL = getattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL', '/')

class AutoLoginViewError(Exception):
    """A problem in the auto login view."""
    pass

class AutoLoginView(View):
    """
    Get an hash_code (md5,sha1, etc.. driven by settings) and try to match against all suth.User,
    at the first match authenticate it for the session.

    To use this view is essential in url to use the kwarg: autologincode
    es. in urls.py:
       url(r'auto/(?P<autologincode>\w+)')
    really needed that autologincode will put in self.kwargs
    """
    hash_func_types = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
    autologincode = None
    hash_func_name = None
    hash_func = lambda x: None

    def _check_and_set_hash_func(self, hfname):
        if not isinstance(hfname, basestring):
            setattr(self, 'hash_func_name', 'md5')
        else:
            if hfname.lower() in self.hash_func_types:
                setattr(self, 'hash_func_name', hfname.lower())
            else:
                setattr(self, 'hash_func_name', 'md5')

        if hasattr(hashlib, self.hash_func_name) and self.hash_func_name in self.hash_func_types:
            setattr(self, 'hash_func', getattr(hashlib, self.hash_func_name))
            assert(callable(self.hash_func))
        else:
            logger.error("hash function unknown: %s", self.hash_func_name)
            raise AutoLoginViewError("hashlib function unknown: %s", self.hash_func_name)

    def __init__(self, **kwargs):
        super(AutoLoginView, self).__init__(**kwargs)
        if hasattr(self, 'hash_func_name'):
            self._check_and_set_hash_func(self.hash_func_name)
        else:
            self._check_and_set_hash_func(HASH_FUNC_NAME)

    def _get_url_redirect_to(self):
        if hasattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL_NAME'):
            return reverse(getattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL_NAME'))
        return DEFAULT_REDIRECT_URL

    def _get_user_for_code(self, code):
        """
        Return auth.User which hashed username match code or None.
        """
        found = None
        if not callable(self.hash_func):
            raise AutoLoginViewError("Hash function is not callable: %s",
                                     self.hash_func)
        for u in User.objects.filter(is_active=True, is_staff=ALLOW_STAFF, is_superuser=ALLOW_SUPERUSER):
            if code == self.hash_func(u.username).hexdigest():
                found = u
                break
        return found

    def get(self, request, *args, **kwargs):
        next_url = self.request.GET.get('next', self._get_url_redirect_to())
        if self.autologincode is None:
            return HttpResponseRedirect(next_url)
        # have an autologincode
        matched_user = self._get_user_for_code(self.autologincode)
        if matched_user is None:
            logger.warning("No user match autologincode: %s", self.autologincode)
            return HttpResponseRedirect(next_url)
        # have an auth.User to authenticate
        auth.login(self.request, matched_user)
        return HttpResponseRedirect(next_url)
