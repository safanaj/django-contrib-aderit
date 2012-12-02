# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=C0103,W0142,W0201,E1103

# django.contrib.aderit.generic_utils.view -- django.views.generic extensions
#
# Copyright (C) 2012 Aderit srl
#
# Author: Marco Bardelli <marco.bardelli@aderit.it>, <bardelli.marco@gmail.com>
#
# This file is part of DjangoContribAderit.
#
# DjangoContribAderit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DjangoContribAderit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DjangoContribAderit.  If not, see <http://www.gnu.org/licenses/>.

'''Generic Views, extending django.views.generic.View'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''

from django.conf import settings  # for CACHE_MIDDLEWARE_SECONDS
from django.http import HttpResponsePermanentRedirect
from django.utils.log import getLogger
from django.utils.translation import ugettext as _

from django.views.generic import View
try:
    from django.views.decorators.debug import (sensitive_post_parameters,
                                               sensitive_variables)
except ImportError:
    has_decorators_debug = False
else:
    has_decorators_debug = True
from django.views.decorators.cache import (never_cache,
                                           cache_page,
                                           cache_control)
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import (login_required,
                                            permission_required,
                                            user_passes_test)

_DEFAULT_CACHE_TIMEOUT = getattr(settings, 'CACHE_MIDDLEWARE_SECONDS', 3600)
_UNCLEANABLE_COOKIES = getattr(settings,
                               'UNCLEANABLE_COOKIES',
                               ['__utmz', 'sessionid', 'csrftoken', '__utma'])


class GenericUtilUseDecoratorError(Exception):
    """Illegal use of decorators in GenericUtilView"""
    pass

logger = getLogger('aderit.generic_utils.views')


def _setup_attrs(self, debug=False, **attrs):
    '''setattr @attrs on @self'''
    for k in attrs.keys():
        if getattr(self, 'force_setup_attrs', False) or hasattr(self, k):
            setattr(self, k, attrs.get(k))
            if debug is True:
                logger.debug("setattr done: %s ==> %s", k, attrs.get(k))


class GenericUtilView(View):
    '''Decoratable View'''
    debug_dispatch_method = False
    debug_dispatch_method_full = True
    debug_show_response_content = False
    force_setup_attrs = False
    ### stuff for really never_cache an HttpResponse
    force_never_cache = False
    ### Stuff for several decorators
    # debug decorators and them params
    use_sensitive_variables_decorator = False
    sensitive_variables_decorator_args = []
    use_sensitive_post_parameters_decorator = False
    sensitive_post_parameters_decorator_args = []
    # cache decorators and them params
    use_never_cache_decorator = False
    use_cache_page_decorator = False
    cache_page_decorator_timeout = _DEFAULT_CACHE_TIMEOUT
    cache_page_decorator_cache = None
    cache_page_decorator_key_prefix = None
    use_cache_control_decorator = False
    cache_control_decorator_kwargs = {}
    # csrf decorators
    use_csrf_protect_decorator = False
    use_csrf_exempt_decorator = False
    # auth decorators and them params
    common_auth_decorators_login_url = None
    common_auth_decorators_redirect_field_name = ""
    use_login_required_decorator = False
    login_required_decorator_login_url = None
    login_required_decorator_redirect_field_name = REDIRECT_FIELD_NAME
    use_permission_required_decorator = False
    permission_required_decorator_perm = None
    permission_required_decorator_raise = False
    use_user_passes_test_decorator = False
    ### no test_func shold be raise ???
    user_passes_test_decorator_test_func = lambda u: True
    user_passes_test_decorator_login_url = None
    user_passes_test_decorator_redirect_field_name = REDIRECT_FIELD_NAME

    ### Stuff to clean cookies
    clean_response_cookies = False
    exclude_clean_cookies = None
    only_clean_cookies = None

    def _clean_response_cookies(self, response):
        '''remove cookies from response'''
        _exclude = []
        if isinstance(self.exclude_clean_cookies, tuple):
            _exclude += list(self.exclude_clean_cookies)
        elif isinstance(self.exclude_clean_cookies, list):
            _exclude += self.exclude_clean_cookies
        _only = []
        if isinstance(self.only_clean_cookies, tuple):
            _only += list(self.only_clean_cookies)
        elif isinstance(self.only_clean_cookies, list):
            _only += self.only_clean_cookies
        _uncleanable = []
        if isinstance(_UNCLEANABLE_COOKIES, tuple):
            _uncleanable += list(_UNCLEANABLE_COOKIES)
        elif isinstance(_UNCLEANABLE_COOKIES, list):
            _uncleanable += _UNCLEANABLE_COOKIES
        uncleanable_cookies = _uncleanable + _exclude
        clean_cookies = _only or response.cookies.keys()
        _cookies = set(clean_cookies) - set(uncleanable_cookies)
        for c in list(_cookies):
            response.delete_cookie(c)

    def _maybe_decorate_sensitive(self, handler):
        '''sensitive related decorators'''
        if self.use_sensitive_variables_decorator:
            _args = self.sensitive_variables_decorator_args
            handler = sensitive_variables(*_args)(handler)
            if self.debug_dispatch_method:
                logger.debug("sensitive_variables decoration done")
        if self.use_sensitive_post_parameters_decorator:
            _args = self.sensitive_post_parameters_decorator_args
            handler = sensitive_post_parameters(*_args)(handler)
            if self.debug_dispatch_method:
                logger.debug("sensitive_post_parameters decoration done")

    def _maybe_decorate_cache(self, handler):
        '''cache related decorators'''
        # think about sense and compatibility combination for cache decorators,
        # precedence: never_cache, cache_page, cache_control
        if self.use_never_cache_decorator:
            handler = never_cache(handler)
            if self.debug_dispatch_method:
                logger.debug("never_cache decoration done")
        if not self.use_never_cache_decorator and \
                self.use_cache_page_decorator:
            _timeout = self.cache_page_decorator_timeout
            _cache = self.cache_page_decorator_cache
            _kp = self.cache_page_decorator_key_prefix
            handler = cache_page(_timeout, cache=_cache,
                                 key_prefix=_kp)(handler)
            if self.debug_dispatch_method:
                logger.debug("cache_page decoration done")
        _use_cache_control = bool(not self.use_never_cache_decorator)
        _use_cache_control &= bool(not self.use_cache_page_decorator)
        _use_cache_control &= bool(self.use_cache_control_decorator)
        if _use_cache_control:
            _kw = self.cache_control_decorator_kwargs
            handler = cache_control(**_kw)(handler)
            if self.debug_dispatch_method:
                logger.debug("cache_control decoration done")

    def _maybe_decorate_csrf(self, handler):
        '''csrf related decorators'''
        # csrf are simple, but usually
        # you want protect and occasionally exempt,
        # which exempt has precedence
        if self.use_csrf_protect_decorator and \
                not self.use_csrf_exempt_decorator:
            handler = csrf_protect(handler)
            if self.debug_dispatch_method:
                logger.debug("csrf_protect decoration done")
        elif self.use_csrf_exempt_decorator:
            handler = csrf_exempt(handler)
            if self.debug_dispatch_method:
                logger.debug("csrf_exempt decoration done")

    def _decorate_handler(self, handler):
        '''helper method to decorate dispach'''
        self._maybe_decorate_sensitive(handler)
        self._maybe_decorate_cache(handler)
        self._maybe_decorate_csrf(handler)

        # auth decorators, think about the order, becase last redirection win
        if self.common_auth_decorators_login_url is not None:
            _clu = self.common_auth_decorators_login_url
            self.login_required_decorator_login_url = _clu
            self.permission_required_decorator_login_url = _clu
            self.user_passes_test_decorator_login_url = _clu
            if self.debug_dispatch_method:
                logger.debug("auth decorators use common login_url=%s", _clu)

        if self.common_auth_decorators_redirect_field_name:
            _crfn = self.common_auth_decorators_redirect_field_name
            self.login_required_decorator_redirect_field_name = _crfn
            self.permission_required_decorator_redirect_field_name = _crfn
            self.user_passes_test_decorator_redirect_field_name = _crfn
            if self.debug_dispatch_method:
                logger.debug("auth decorators use redirect_field_name=%s",
                             _crfn)

        if self.use_login_required_decorator:
            _rfn = self.login_required_decorator_redirect_field_name
            _lu = self.login_required_decorator_login_url
            handler = login_required(handler, redirect_field_name=_rfn,
                                     login_url=_lu)
            if self.debug_dispatch_method:
                logger.debug("login_required decoration done")
        if self.use_permission_required_decorator:
            if self.permission_required_decorator_perm is None:
                raise \
                    GenericUtilUseDecoratorError(_("Give a perm to decorator"))
            _perm = self.permission_required_decorator_perm
            _rfn = self.permission_required_decorator_redirect_field_name
            _lu = self.permission_required_decorator_login_url
            handler = permission_required(_perm, login_url=_lu)(handler)
            if self.debug_dispatch_method:
                logger.debug("permission_required decoration done")
        if self.use_user_passes_test_decorator:
            _test_fn = self.user_passes_test_decorator_test_func
            _rfn = self.user_passes_test_decorator_redirect_field_name
            _lu = self.user_passes_test_decorator_login_url
            handler = user_passes_test(_test_fn, redirect_field_name=_rfn,
                                       login_url=_lu)(handler)
            if self.debug_dispatch_method:
                logger.debug("user_passes_test decoration done")
        return handler

    def setup_attrs(self, **kwargs):
        '''set kwargs in instance attribute.
        before dispatch method
        '''
        if self.debug_dispatch_method:
            logger.debug("setup_attrs forced: %s", self.force_setup_attrs)
        debug_setup_attrs = self.debug_dispatch_method
        debug_setup_attrs &= self.debug_dispatch_method_full
        _setup_attrs(self, debug=debug_setup_attrs, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if self.debug_dispatch_method and self.debug_dispatch_method_full:
            logger.debug("request: %s", request)
        if self.debug_dispatch_method:
            logger.debug("args: %s", args)
            logger.debug("kwargs: %s", kwargs)
        if hasattr(self, 'setup_attrs'):
            self.setup_attrs(**kwargs)
            if self.debug_dispatch_method:
                logger.debug("custom setup_attrs done with kwargs: %s", kwargs)
        else:
            debug_setup_attrs = self.debug_dispatch_method
            debug_setup_attrs &= self.debug_dispatch_method_full
            _setup_attrs(self, debug=debug_setup_attrs, **kwargs)
            if self.debug_dispatch_method:
                logger.debug("standard setup_attrs done with kwargs: %s",
                             kwargs)

        decorated = \
            self._decorate_handler(super(GenericUtilView, self).dispatch)
        response = decorated(request, *args, **kwargs)
        if self.force_never_cache:
            from django.utils.cache import add_never_cache_headers
            add_never_cache_headers(response)
        if self.debug_dispatch_method:
            logger.debug("response headers: %s", response.items())
            logger.debug("response cookies: %s", response.cookies.output())
            if self.debug_dispatch_method_full:
                logger.debug("response cookies in js:\n%s\n",
                             response.cookies.js_output())
                if self.debug_show_response_content:
                    if not getattr(response, 'is_rendered', True):
                        response.render()
                    logger.debug("response content:\n%s\n", response.content)

        if self.clean_response_cookies:
            self._clean_response_cookies(response)
        return response


class GenericProtectedView(GenericUtilView):
    '''GenericUtilsView decorated with:
    sensitive_post_parameters and csrf_protect
    '''
    use_sensitive_post_parameters_decorator = has_decorators_debug
    use_csrf_protect_decorator = True


class GenericUncacheableView(GenericUtilView):
    '''GenericUtilsView decorated with:
    never_cache
    '''
    use_never_cache_decorator = True


class GenericProtectedUncacheableView(GenericUtilView):
    '''GenericUtilsView decorated with:
    sensitive_post_parameters
    csrf_protect
    never_cache
    '''
    use_sensitive_post_parameters_decorator = has_decorators_debug
    use_csrf_protect_decorator = True
    use_never_cache_decorator = True

### todo: implementare GenericFormView, GenericCreateView,
###       GenericUpdateView, GenericDeleteView
###       per mettere `action_url' e `submit_label' nel contesto
###       via `get_context_data'


### others simple view
def external_view(request, target):
    '''redirect permanently to @target.

    (comodo per django cms nelle impostazioni avanzate,
    il redirect ad una pagina)
    example usage:

    in urls.py
    from django.contrib.aderit.generic_utils.views import external_view

    urlpatterns = (
      url(r'^offsite/(?P<target>.+)$', external_view),
    )
    '''
    logger.debug("external_view: request'd path: %s", request.path)
    return HttpResponsePermanentRedirect('http://' + target)
