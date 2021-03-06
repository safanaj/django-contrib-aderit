# pylint: disable-msg=C0301,C0103,C0111,W0232,W0613,E1101,R0903
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# models.py -- python module for auth/user profile model
#
# Copyright (C) 2012 Aderit srl
#
# Authors: Marco Bardelli <marco.bardelli@aderit.it>,
#                         <bardelli.marco@gmail.com>
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
'''User profile abstract model'''

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.aderit.access_account import \
    _get_model_from_auth_profile_module


class AccessAccount(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=128, blank=True)

    class Meta:
        abstract = True
        ordering = ["user"]

    def __unicode__(self):
        return self.user.username

    def save(self, force_insert=False, force_update=False, using=None):
        if self.pk is not None:
            self.user.save(force_insert=force_insert,
                           force_update=force_update,
                           using=using)
        super(AccessAccount, self).save(force_insert=force_insert,
                                        force_update=force_update, using=using)

    def _set_username(self, value):
        self.user.username = value

    def _get_username(self):
        return self.user.username

    username = property(_get_username, _set_username)

    def _set_email(self, value):
        self.user.email = value

    def _get_email(self):
        return self.user.email

    email = property(_get_email, _set_email)

    def _set_firstname(self, value):
        self.user.first_name = value

    def _get_firstname(self):
        return self.user.first_name

    firstname = property(_get_firstname, _set_firstname)

    def _set_lastname(self, value):
        self.user.last_name = value

    def _get_lastname(self):
        return self.user.last_name

    lastname = property(_get_lastname, _set_lastname)

    @property
    def fullname(self):
        _fullname = ""
        if self.firstname != "":
            _fullname += self.firstname
        if self.lastname != "":
            _fullname += " " + self.lastname
        if _fullname == "":
            _fullname = self.username
        return _fullname

    def _set_is_staff(self, value):
        self.user.is_staff = value

    def _get_is_staff(self):
        return self.user.is_staff

    is_staff = property(_get_is_staff, _set_is_staff)

    def _set_is_admin(self, value):
        self.user.is_admin = value

    def _get_is_admin(self):
        return self.user.is_admin

    is_admin = property(_get_is_admin, _set_is_admin)

    def _set_is_active(self, value):
        self.user.is_active = value

    def _get_is_active(self):
        return self.user.is_active

    is_active = property(_get_is_active, _set_is_active)

    @property
    def usergroups(self):
        return self.user.groups.all()

    @property
    def userpermissions(self):
        return self.user.user_permissions.all()

    @property
    def last_login(self):
        return self.user.last_login

    @property
    def date_joined(self):
        return self.user.date_joined


def create_access_account(sender, instance, created, **kwargs):
    if created:
        model = _get_model_from_auth_profile_module()
        model(user=instance).save()

post_save.connect(create_access_account, sender=User)
