__doc__ = '''Generic model fields'''

from django.utils.translation import ugettext_lazy as _

from django.db.models.fields import CharField
from django.contrib.aderit.generic_utils.forms import fields as forms_fields

class GenericPhoneField(CharField):
    description = _("Phone number")

    def formfield(self, **kwargs):
        defaults = {
            'form_class' : forms_fields.GenericPhoneField
            }
        defaults.update(kwargs)
        return super(GenericPhoneField, self).formfield(**defaults)

