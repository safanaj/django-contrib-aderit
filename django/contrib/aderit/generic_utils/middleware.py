__doc__ = '''Generic middlewares'''

from django.conf import settings

### currentUserMiddleware
USER_ATTR_NAME = getattr(settings, 'LOCAL_USER_ATTR_NAME', '_current_user')

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
_thread_locals = local()

from new import instancemethod
def _do_set_current_user(user_fun):
    setattr(_thread_locals, USER_ATTR_NAME, instancemethod(user_fun, _thread_locals, type(_thread_locals)))

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
        is_mobile = False;

        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']

            # Test common mobile values.
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)

            if match:
                is_mobile = True;
            else:
                # Nokia like test for WAP browsers.
                # http://www.developershome.com/wap/xhtmlmp/xhtml_mp_tutorial.asp?page=mimeTypesFileExtension

                if request.META.has_key('HTTP_ACCEPT'):
                    http_accept = request.META['HTTP_ACCEPT']

                    pattern = "application/vnd\.wap\.xhtml\+xml"
                    prog = re.compile(pattern, re.IGNORECASE)

                    match = prog.search(http_accept)

                    if match:
                        is_mobile = True

            if not is_mobile:
                # Now we test the user_agent from a big list.
                user_agents_test = ("w3c ", "acs-", "alav", "alca", "amoi", "audi",
                                    "avan", "benq", "bird", "blac", "blaz", "brew",
                                    "cell", "cldc", "cmd-", "dang", "doco", "eric",
                                    "hipt", "inno", "ipaq", "java", "jigs", "kddi",
                                    "keji", "leno", "lg-c", "lg-d", "lg-g", "lge-",
                                    "maui", "maxo", "midp", "mits", "mmef", "mobi",
                                    "mot-", "moto", "mwbp", "nec-", "newt", "noki",
                                    "xda",  "palm", "pana", "pant", "phil", "play",
                                    "port", "prox", "qwap", "sage", "sams", "sany",
                                    "sch-", "sec-", "send", "seri", "sgh-", "shar",
                                    "sie-", "siem", "smal", "smar", "sony", "sph-",
                                    "symb", "t-mo", "teli", "tim-", "tosh", "tsm-",
                                    "upg1", "upsi", "vk-v", "voda", "wap-", "wapa",
                                    "wapi", "wapp", "wapr", "webc", "winw", "winw",
                                    "xda-",)

                test = user_agent[0:4].lower()
                if test in user_agents_test:
                    is_mobile = True

        request.is_mobile = is_mobile
