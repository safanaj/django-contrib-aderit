# pylint: disable-msg=C0301,C0103,E1101,W0212
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# backends.py -- python module for auth backends
#
# Copyright (C) 2012 Aderit srl
#
# Authors: Marco Bardelli <marco.bardelli@aderit.it>,
#                         <bardelli.marco@gmail.com>
#          Michele Pellegrini <michele.pellegini@aderit.it>
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
'''Authentication backends'''

from django.utils.log import getLogger
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator

from django.contrib.aderit.access_account import \
    _get_model_from_auth_profile_module
from django.contrib.aderit.access_account.tokens import \
    check_random_token_is_valid

logger = getLogger('aderit.access_account.auth_backend')


class TokenBackend(object):
    """
    Backend for authentication via token
    """

    supports_inactive_user = False

    def authenticate(self, token=None, user=None):
        """
        Se non posso cercare il @token nel DB
        (il modello non ha il campo token) ed ho @user
        provo default_token_generator.check_token

        Se posso cercarlo sul DB:
          1 - lo trovo:
              + @user passato deve corrispondere al @token trovato sul DB
          2 - non lo trovo:
              + provo usando default_token_generator.check_token

        Se @user e' passato ma non ha l'attributo last_login
        (usato nel chek_token), non autentico.
        """
        logger.debug("authenticate[%s] ( token=%s , user=%s )",
                     self, token, user)
        if token is not None:
            model = _get_model_from_auth_profile_module()
            if 'token' in [f.name for f in model._meta.fields]:
                try:
                    user_profile = model.objects.get(token=token)
                    if user is None and check_random_token_is_valid(token):
                        return user_profile.user
                    elif user == user_profile.user and \
                            check_random_token_is_valid(token):
                        return user
                except model.MultipleObjectsReturned:
                    logger.error("token[\"%s\"] is not unique", token)
                    return None
                except model.DoesNotExist:
                    try:
                        if user is not None and \
                                default_token_generator.\
                                check_token(user, token):
                            logger.debug("token DoenNotExist but "
                                         "(user: %s , token: %s) "
                                         "is valid, auth OK",
                                         user, token)
                            return user
                    except AttributeError, e:
                        logger.error("user[%s] can not be "
                                     "authenticate: %s", user, e)
            else:
                try:
                    if user is not None and \
                            default_token_generator\
                            .check_token(user, token):
                        logger.debug("model[%s] have not token field "
                                     "(user: %s , token: %s) is valid,"
                                     " auth OK",
                                     model, user, token)
                        return user
                except AttributeError:
                    logger.error("user[%s] can not be authenticate: %s",
                                 user, e)
        logger.debug("authenticate ( token=%s , user=%s ), fail", token, user)
        return None

    def get_user(self, user_id):
        """
        Return User with @user_id (pk) from database
        """
        logger.debug("get_user[%s] ( user_id=%s )", self, user_id)
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
