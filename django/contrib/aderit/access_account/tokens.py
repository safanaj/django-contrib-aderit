# pylint: disable-msg=C0301,C0103,E1101,W0212,W0402
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# tokens.py -- random token generation
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
'''Generate random token for authentication'''

from django.conf import settings
from django.utils.http import int_to_base36, base36_to_int
import random
import string
import time

TOKEN_DURATION_SECONDS = \
    getattr(settings, 'ACCESS_ACCOUNT_TOKEN_DURATION_SECONDS', 3600 * 48)


def make_random_unexpirable_token(len_random_part=32):
    population = string.ascii_letters + string.digits
    return "".join(random.sample(population, len_random_part))


def make_random_expirable_token(len_random_part=32):
    random_part = \
        make_random_unexpirable_token(len_random_part=len_random_part)
    prefix_part = int_to_base36(int(time.time()))
    return "%s-%s" % (prefix_part, random_part)


def random_token_is_expired(token):
    splitted = token.split('-', 1)
    splitted_len = len(splitted)
    if splitted_len == 1:
        ## no prefix for timestamp, unexpirable
        return False
    else:  # splitted_len is 2, check for exipration
        return (int(time.time()) - base36_to_int(splitted[0])) > \
            TOKEN_DURATION_SECONDS


def check_random_token_is_valid(token):
    return not random_token_is_expired(token)
