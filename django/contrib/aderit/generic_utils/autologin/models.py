from django.conf import settings
from django.db import models
from django.db.models import fields
from django.contrib.auth.models import User
import logging

logger = logging.getLogger("aderit.generic_utils.autologin.models")

# For AutoLogin more secure
class AutoLoginCodeModel(models.Model):
    """
    """
    user = models.OneToOneField(User)
    code = models.CharField("Auto login code", max_length=256, editable=False)
    
    class Meta:
        verbose_name = 'Auto login code'
        verbose_name_plural = 'Auto login codes'
        ordering = ['user']

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

