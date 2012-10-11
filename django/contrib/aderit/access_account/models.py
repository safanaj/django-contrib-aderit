# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.db import models
from django.contrib.auth.models import User

class AccessAccount(models.Model):
    user = models.OneToOneField(User)

    class Meta:
        abstract = True
        ordering = ["user"]

    def __unicode__(self):
        return self.user.username

    def save(self, force_insert=False, force_update=False, using=None):
        if self.pk is not None:
            self.user.save(force_insert=force_insert, force_update=force_update, using=using)
        super(AccessAccount, self).save(force_insert=force_insert, force_update=force_update, using=using)

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
        return "%s %s" % (self.firstname, self.lastname)

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
