# pylint: disable-msg=C0301,C0103
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# django.contrib.aderit.access_account -- python module for auth management
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
'''User profile management'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''

from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable
from django.utils.translation import ugettext as _
from django.db.models.loading import get_model


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
    app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
    return get_model(app_label, model_name)
