from django.contrib.aderit.generic_utils.autologin.models import AutoLoginCodeModel
from django.contrib.aderit.generic_utils.autologin.views import make_hash_code
import logging
import hashlib
import random
import string

logger = logging.getLogger('aderit.generic_utils.autologin.utils')

def gen_autologin_rand_code(modeladmin, request, queryset):
    s = string.letters + string.digits
    for u in queryset:
        ret = ''
        for i in range(0, 50):
            ret += s[int(random.random() * 1000 % len(s))]
        try:
            AutoLoginCodeModel.objects.get_or_create(user=u, code=ret)
        except Exception, e:
            AutoLoginCodeModel.objects.all()
            logger.error("EXC: %s --- during AutoLoginCodeModel creation for %s: with %s", e, u, ret)
gen_autologin_rand_code.short_description = "Generate autologin codes using random of 50 bytes"

def _gen_hash_code(modeladmin, request, queryset):
    from django.conf import settings
    use_secret = getattr(settings, 'AUTOLOGIN_USE_SECRET_KEY', True)
    secret = getattr(settings, 'SECRET_KEY', '')
    hash_func_name = getattr(settings, 'AUTOLOGIN_HASH_FUNC_NAME', 'md5')
    hash_func = None
    if hasattr(hashlib, hash_func_name) and hash_func_name in ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']:
        hash_func = getattr(hashlib, hash_func_name)
        assert(callable(hash_func))
        logger.debug("HFUNC: %s", hash_func_name)
    for u in queryset:
        string_base = ''
        if hasattr(u, 'username'):
            string_base += u.username
            if use_secret:
                string_base += secret
            try:
                AutoLoginCodeModel(user=u,
                                   code=make_hash_code(hash_func=hash_func,
                                                       string_base=string_base)).save()
            except Exception, e:
                logger.error("EXC: %s --- during AutoLoginCodeModel creation for %s: with %s func named %s",
                             e, u, hash_func, hash_func_name)
_gen_hash_code.short_description = "Generate autologin codes using hashlib"

def _add_action_to_admin_user(action_func=None):
    from django.contrib.auth.admin import UserAdmin
    from django.contrib import admin 
    from django.contrib.auth.models import User
    if not callable(action_func):
        logger.debug("Nothing to add to UserAdmin actions: %s", action_func)
        return
    user_admin_class = admin.site._registry.get(User, None)
    if user_admin_class is not None and action_func not in user_admin_class.actions:
        user_admin_class.actions.append(action_func)
        logger.debug("Added actions: %s", action_func)

def add_admin_auth_user_action(action_func=None):
    """
    usually called after admin.autodiscover() in urls.py
    """
    if action_func is None:
        action_func = _gen_hash_code
    _add_action_to_admin_user(action_func=action_func)

