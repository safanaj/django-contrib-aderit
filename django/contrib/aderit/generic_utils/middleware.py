# pylint: disable-msg=F0401,C0301,C0103,E0611,R0903
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# middleware.py -- some utils middlewares
#
# Copyright (C) 2012 Aderit srl
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
'''Generic middlewares'''

from django.conf import settings
from django.utils.log import getLogger

logger = getLogger('aderit.generic_utils.middleware')

### currentUserMiddleware
USER_ATTR_NAME = getattr(settings, 'LOCAL_USER_ATTR_NAME', '_current_user')

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
_thread_locals = local()

from new import instancemethod


def _do_set_current_user(user_fun):
    setattr(_thread_locals, USER_ATTR_NAME,
            instancemethod(user_fun, _thread_locals, type(_thread_locals)))


def _set_current_user(user=None):
    '''
    Sets current user in local thread.

    Can be used as a hook e.g. for shell jobs (when request object is not
    available).
    '''
    _do_set_current_user(lambda self: user)


class LocalUserMiddleware(object):
    def process_request(self, request):
        # request.user closure; asserts laziness; memoization is implemented in
        # request.user (non-data descriptor)
        logger.debug("process_request[%s]", self)
        _do_set_current_user(lambda self: getattr(request, 'user', None))


def get_current_user():
    current_user = getattr(_thread_locals, USER_ATTR_NAME, None)
    return current_user() if current_user else current_user

### langMiddleware
from django.utils.cache import patch_vary_headers
from django.utils import translation


class SessionBasedLocaleMiddleware(object):
    """
    This Middleware saves the desired content language in the user session.
    The SessionMiddleware has to be activated.
    """
    def process_request(self, request):
        logger.debug("process_request[%s]", self)
        if request.method == 'GET' and 'lang' in request.GET:
            language = request.GET['lang']
            request.session['language'] = language
        elif 'language' in request.session:
            language = request.session['language']
        else:
            language = translation.get_language_from_request(request)

        for lang in settings.LANGUAGES:
            if lang[0] == language:
                translation.activate(language)

        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        logger.debug("process_response[%s] - reqest: %s", self, request.path)
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response

### mobileMiddleware
import re


class MobileDetectionMiddleware(object):
    """
    Useful middleware to detect if the user is
    on a mobile device.
    """

    def process_request(self, request):
        logger.debug("process_request[%s]", self)
        is_mobile = False

        if 'HTTP_USER_AGENT' in request.META:
            user_agent = request.META['HTTP_USER_AGENT']

            # Test common mobile values.
            pattern = r"(up.browser|up.link|mmp|symbian"\
                "|smartphone|midp|wap|phone|windows ce"\
                "|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)

            if match:
                is_mobile = True
            else:
                # Nokia like test for WAP browsers.
                # http://www.developershome.com/wap/xhtmlmp
                # /xhtml_mp_tutorial.asp?page=mimeTypesFileExtension

                if 'HTTP_ACCEPT' in request.META:
                    http_accept = request.META['HTTP_ACCEPT']

                    pattern = r"application/vnd\.wap\.xhtml\+xml"
                    prog = re.compile(pattern, re.IGNORECASE)

                    match = prog.search(http_accept)

                    if match:
                        is_mobile = True

            if not is_mobile:
                # Now we test the user_agent from a big list.
                user_agents_test = ("w3c ", "acs-", "alav", "alca", "amoi",
                                    "audi", "avan", "benq", "bird", "blac",
                                    "blaz", "brew", "cell", "cldc", "cmd-",
                                    "dang", "doco", "eric", "hipt", "inno",
                                    "ipaq", "java", "jigs", "kddi", "keji",
                                    "leno", "lg-c", "lg-d", "lg-g", "lge-",
                                    "maui", "maxo", "midp", "mits", "mmef",
                                    "mobi", "mot-", "moto", "mwbp", "nec-",
                                    "newt", "noki", "xda", "palm", "pana",
                                    "pant", "phil", "play", "port", "prox",
                                    "qwap", "sage", "sams", "sany", "sch-",
                                    "sec-", "send", "seri", "sgh-", "shar",
                                    "sie-", "siem", "smal", "smar", "sony",
                                    "sph-", "symb", "t-mo", "teli", "tim-",
                                    "tosh", "tsm-", "upg1", "upsi", "vk-v",
                                    "voda", "wap-", "wapa", "wapi", "wapp",
                                    "wapr", "webc", "winw", "winw", "xda-")

                test = user_agent[0:4].lower()
                if test in user_agents_test:
                    is_mobile = True

        request.is_mobile = is_mobile
