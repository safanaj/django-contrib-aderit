from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.generic import View
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.contrib.aderit.generic_utils.views import GenericUtilView
import hashlib
import logging

logger = logging.getLogger("aderit.generic_utils.views.autologin")

ALLOW_ONLY_FOR_GROUPNAME = getattr(settings, 'AUTOLOGIN_ALLOW_ONLY_FOR_GROUPNAME', None)
ALLOW_ONLY_USERS = getattr(settings, 'AUTOLOGIN_ALLOW_ONLY_USERS', None)
ALLOW_SUPERUSER = getattr(settings, 'AUTOLOGIN_ALLOW_SUPERUSER', False)
ALLOW_STAFF = getattr(settings, 'AUTOLOGIN_ALLOW_STAFF', False)
EXCLUDE_USERS = getattr(settings, 'AUTOLOGIN_EXCLUDE_USERS', [])
USE_MODEL = getattr(settings, 'AUTOLOGIN_USE_MODEL', False) # TODO implementation
HASH_FUNC_NAME = getattr(settings, 'AUTOLOGIN_HASH_FUNC_NAME', 'md5')
DEFAULT_REDIRECT_URL = getattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL', '/')
URL_PATTERN_TOKEN = getattr(settings, 'AUTOLOGIN_URL_PATTERN_TOKEN', 'autologincode')
USE_SECRET_KEY = getattr(settings, 'AUTOLOGIN_USE_SECRET_KEY', True)


FALLBACK_AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'
FALLBACK_SECRET_KEY = 'deadbeaf' * 5

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
    if you want to use an other pattern token name set AUTOLOGIN_URL_PATTERN_TOKEN in settings (default is: "autologincode")
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
        if getattr(self, 'hash_func_name', None) is not None:
            self._check_and_set_hash_func(self.hash_func_name)
        else:
            self._check_and_set_hash_func(HASH_FUNC_NAME)

    def _get_url_redirect_to(self):
        if hasattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL_NAME'):
            return reverse(getattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL_NAME'))
        return DEFAULT_REDIRECT_URL

    def _get_user_for_code_in_model(self, code):
        return None

    def _get_user_for_code(self, code):
        """
        Return auth.User which hashed username match code or None.
        """
        found = None
        users_qs = None
        if not callable(self.hash_func):
            raise AutoLoginViewError("Hash function is not callable: %s",
                                     self.hash_func)
        if USE_MODEL:
            return self._get_user_for_code_in_model(code)

        if ALLOW_ONLY_FOR_GROUPNAME is not None:
            try:
                group = Group.objects.get(name=ALLOW_ONLY_FOR_GROUPNAME)
            except:
                #raise AutoLoginViewError("Group: %s -- does not exists!", ALLOW_ONLY_FOR_GROUPNAME)
                logger.error("Group: %s -- does not exists!", ALLOW_ONLY_FOR_GROUPNAME)
            else:
                users_qs = group.user_set.all()
        if users_qs is None:
            users_qs = User.objects.filter(is_active=True)
        else:
            users_qs = users_qs.filter(is_active=True)

        if ALLOW_ONLY_USERS is not None and hasattr(ALLOW_ONLY_USERS, '__iter__'):
            users_qs = users_qs.filter(username__in=ALLOW_ONLY_USERS)

        if len(EXCLUDE_USERS) > 0:
            users_qs = users_qs.exclude(username__in=EXCLUDE_USERS)

        if ALLOW_STAFF is False:
            users_qs = users_qs.filter(is_staff=False)

        if ALLOW_SUPERUSER is False:
            users_qs = users_qs.filter(is_superuser=False)

        for u in users_qs:
            _string_base_ = u.username
            if USE_SECRET_KEY:
                _string_base_ += getattr(settings, 'SECRET_KEY', FALLBACK_SECRET_KEY)
            if code == self.hash_func(_string_base_).hexdigest():
                found = u
                break
        return found

    def get(self, request, *args, **kwargs):
        next_url = self.request.GET.get('next', self._get_url_redirect_to())
        # setup autologincode
        self.autologincode = self.kwargs.get(URL_PATTERN_TOKEN, None)
        if self.autologincode is None:
            logger.debug("W: self.autologincode is None")
            return HttpResponseRedirect(next_url)
        # have an autologincode
        matched_user = self._get_user_for_code(self.autologincode)
        if matched_user is None:
            logger.warning("No user match autologincode: %s", self.autologincode)
            return HttpResponseRedirect(next_url)
        # have an auth.User to authenticate
	_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        if len(_backends) > 0:
            matched_user.backend = _backends[0]
        else:
            matched_user.backend = FALLBACK_AUTH_BACKEND
        auth.login(self.request, matched_user)
        return HttpResponseRedirect(next_url)

class AutoLoginView2(GenericUtilView):
    """
    Get an hash_code (md5,sha1, etc.. driven by settings) and try to match against all suth.User,
    at the first match authenticate it for the session.

    To use this view is essential in url to use the kwarg: autologincode
    es. in urls.py:
       url(r'auto/(?P<autologincode>\w+)')
    really needed that autologincode will put in self.kwargs
    if you want to use an other pattern token name set AUTOLOGIN_URL_PATTERN_TOKEN in settings (default is: "autologincode")
    """
    force_setup_attrs = True
    hash_func_types = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
    autologincode = None
    hash_func_name = getattr(settings, 'AUTOLOGIN_HASH_FUNC_NAME', 'md5')
    hash_func = lambda x: None
    allow_only_for_groupname = getattr(settings, 'AUTOLOGIN_ALLOW_ONLY_FOR_GROUPNAME', None)
    allow_only_users = getattr(settings, 'AUTOLOGIN_ALLOW_ONLY_USERS', None)
    allow_superuser = getattr(settings, 'AUTOLOGIN_ALLOW_SUPERUSER', False)
    allow_staff = getattr(settings, 'AUTOLOGIN_ALLOW_STAFF', False)
    exclude_users = getattr(settings, 'AUTOLOGIN_EXCLUDE_USERS', [])
    use_model = getattr(settings, 'AUTOLOGIN_USE_MODEL', False) # TODO implementation
    default_redirect_url = getattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL', '/')
    url_pattern_token = getattr(settings, 'AUTOLOGIN_URL_PATTERN_TOKEN', 'autologincode')
    use_secret_key = getattr(settings, 'AUTOLOGIN_USE_SECRET_KEY', True)

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
        self._check_and_set_hash_func(self.hash_func_name)

    def _get_url_redirect_to(self):
        if hasattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL_NAME'):
            return reverse(getattr(settings, 'AUTOLOGIN_DEFAULT_REDIRECT_URL_NAME'))
        return self.default_redirect_url

    def _get_user_for_code_in_model(self, code):
        return None

    def _get_user_for_code(self, code):
        """
        Return auth.User which hashed username match code or None.
        """
        found = None
        users_qs = None
        if not callable(self.hash_func):
            raise AutoLoginViewError("Hash function is not callable: %s",
                                     self.hash_func)
        if self.use_model:
            return self._get_user_for_code_in_model(code)

        if self.allow_only_for_groupname is not None:
            try:
                group = Group.objects.get(name=self.allow_only_for_groupname)
            except:
                #raise AutoLoginViewError("Group: %s -- does not exists!", ALLOW_ONLY_FOR_GROUPNAME)
                logger.error("Group: %s -- does not exists!", self.allow_only_for_groupname)
            else:
                users_qs = group.user_set.all()
        if users_qs is None:
            users_qs = User.objects.filter(is_active=True)
        else:
            users_qs = users_qs.filter(is_active=True)

        if self.allow_only_users is not None and hasattr(self.allow_only_users, '__iter__'):
            users_qs = users_qs.filter(username__in=self.allow_only_users)

        if len(self.exclude_users) > 0:
            users_qs = users_qs.exclude(username__in=self.exclude_users)

        if self.allow_staff is False:
            users_qs = users_qs.filter(is_staff=False)

        if self.allow_superuser is False:
            users_qs = users_qs.filter(is_superuser=False)

        for u in users_qs:
            _string_base_ = u.username
            if self.use_secret_key:
                _string_base_ += getattr(settings, 'SECRET_KEY', FALLBACK_SECRET_KEY)
            if code == self.hash_func(_string_base_).hexdigest():
                found = u
                break
        return found

    def get(self, request, *args, **kwargs):
        next_url = self.request.GET.get('next', self._get_url_redirect_to())
        # setup autologincode
        #self.autologincode = self.kwargs.get(URL_PATTERN_TOKEN, None)
        if self.autologincode is None:
            self.autoinclude = getattr(self, self.url_pattern_token, None)
        if self.autologincode is None:
            logger.debug("W: self.autologincode is None")
            return HttpResponseRedirect(next_url)
        # have an autologincode
        matched_user = self._get_user_for_code(self.autologincode)
        if matched_user is None:
            logger.warning("No user match autologincode: %s", self.autologincode)
            return HttpResponseRedirect(next_url)
        # have an auth.User to authenticate
	_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        if len(_backends) > 0:
            matched_user.backend = _backends[0]
        else:
            matched_user.backend = FALLBACK_AUTH_BACKEND
        auth.login(self.request, matched_user)
        return HttpResponseRedirect(next_url)
