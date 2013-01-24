import csv, re

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.log import getLogger
from django.contrib.aderit.questionnaire_extensions.models import CSVQuestImporter

logger = getLogger('aderit.questionnaire_extensions.forms')

class CSVQuestImporterForm(forms.ModelForm):
    class Meta:
        model = CSVQuestImporter

    # def clean(self):
    #     if not str(self.cleaned_data.get('csv_import'))[-4:].upper() == ".CSV":
    #         raise ValidationError(_("File di tipo sbagliato: deve essere *.csv"))
