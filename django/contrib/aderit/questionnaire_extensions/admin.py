# django.contrib.aderit.questionnaire_extensions.admin -- python module
#
# Copyright (C) 2012 Aderit srl
#
# Author: Marco Bardelli <marco.bardelli@aderit.it>,
#                        <bardelli.marco@gmail.com>
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
'''
Admin for Seantis Questionnaire extensions by Aderit.
'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''

from django.contrib import admin
from django.forms import forms, models as forms_models
from django.utils.log import getLogger
from django.contrib.aderit.access_account import _get_model_from_auth_profile_module
from django.contrib.aderit.questionnaire_extensions.models import Questionnaire, QuestionnaireMails

logger = getLogger('aderit.questionnaire_extensions.admin')


# class QuestionnaireAdmin(admin.ModelAdmin):
#     # fields = ('name', 'redirect_url', 'accounts')
#     # fields = ('name', 'redirect_url')
#     # filter_horizontal = ('accounts',)


#     def get_form(self, request, obj=None, **kwargs):
#         logger.debug("get_form: obj %s -- kw: %s -- self.fields: %s",
#                      obj, kwargs, self.fields)
#         form_k = super(QuestionnaireAdmin, self).get_form(request,
#                                                           obj=obj,
#                                                           **kwargs)
#         acc_model = _get_model_from_auth_profile_module()
#         _acc_qs = acc_model.objects.all()
#         if hasattr(obj, 'account_set'):
#             _acc_initial = obj.account_set.all()
#         else:
#             _acc_initial = []
#         _acc_field = forms_models.ModelMultipleChoiceField(_acc_qs,
#                                                            required=False,
#                                                            initial=_acc_initial)
#         form_k.base_fields.update({'accounts': _acc_field})
#         _list_filter_horizontal = list(self.filter_horizontal or [])
#         if 'accounts' not in _list_filter_horizontal:
#             _list_filter_horizontal.append('accounts')
#             self.filter_horizontal = tuple(_list_filter_horizontal)
#             logger.debug("get_form: base_fields %s -- form fields: %s",
#                          form_k.base_fields, self.filter_horizontal)
#         return form_k


class QuestionnaireMailsInline(admin.TabularInline):
    model = QuestionnaireMails
    max_num = 1

class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [QuestionnaireMailsInline]

admin.site.unregister(Questionnaire)
admin.site.register(Questionnaire, QuestionnaireAdmin)
