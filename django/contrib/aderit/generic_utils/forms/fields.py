__doc__ = '''Generic additional form fields (extensions to django.forms.fields)'''

from django.utils.translation import ugettext_lazy as _

from django.forms.fields import RegexField

phone_regex = r'^\+?[0-9]{3}[0-9 ]{5,18}$'

class GenericPhoneField(RegexField):
    default_error_messages = {
        'invalid' : _("Enter a valid phone number.")
        }

    def __init__(self, regex=phone_regex, max_length=None, min_length=None,
                 error_message=None, *args, **kwargs):
        super(GenericPhoneField, self).__init__(regex, max_length=max_length, min_length=min_length,
                                                error_message=error_message, *args, **kwargs)
