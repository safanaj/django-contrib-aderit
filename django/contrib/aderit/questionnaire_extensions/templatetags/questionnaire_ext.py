# django.contrib.aderit.questionnaire_extensions.templatetags.questionnaire_ext.py -- python module
#
# Copyright (C) 2012 Aderit srl
#
# Author: Matteo Atti <matteo.atti@aderit.it>, <attuch@gmail.com>
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
Django Contrib Aderit Questionnaire Extensions templatetags questionnaire_ext.py
'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''


from django import template
from django.utils.log import getLogger

from questionnaire.views import questionset_satisfies_checks
from questionnaire.models import (RunInfo,
                                  Answer,
                                  RunInfoHistory)

from django.contrib.aderit.access_account import _get_model_from_auth_profile_module
logger = getLogger('aderit.questionnaire_extensions'
                   '.templatetags.questionnaire_ext')

register = template.Library()


@register.assignment_tag
def get_prev_questionset(runinfo):
    previous = runinfo.questionset.prev()
    while previous and not questionset_satisfies_checks(previous, runinfo):
        if previous.prev():
            previous = previous.prev()
        else:
            logger.critical("No valid previous QusetionSet "
                            "found: RI: %s - QS: %s",
                            runinfo, runinfo.questionset.sortid)
            break
    return previous

@register.assignment_tag(takes_context=True)
def get_answers(context):
    question = context['question']
    runinfo = context['runinfo']
    try:
        answers = question.answer_set.filter(runid=runinfo.runid, subject=runinfo.subject)
        assert(answers.count() == 1)
        for i in answers:
            return eval(i.answer)
    except Exception, e:
        logger.error("get_answers: %s", e)
    return []

@register.assignment_tag
def users_for_questionnaire(questionnaire):
    account_model = _get_model_from_auth_profile_module()
    subjects = [x for x in account_model.objects.filter(questionnaires__id=questionnaire) if x.subject is not None and x.subject.state == "active"]
    return subjects


@register.simple_tag(takes_context=True)
def get_user_compiled(context, comp_name, not_comp_name):
    context[comp_name] = RunInfoHistory.objects.filter(questionnaire__id=context['object_id'])
    context[not_comp_name] = RunInfo.objects.filter(questionset__questionnaire__id=context['object_id'])
    return ""

@register.simple_tag(takes_context=True)
def show_quest_status_for_subj(context, subjid, qid, kind):
    # completed
    rh = RunInfoHistory.objects.filter(subject__id=int(subjid),
                                       questionnaire__id=int(qid))
    if rh.count() > 0: context[kind] = 'completed'

    # not completed
    ri = RunInfo.objects.filter(subject__id=int(subjid),
                                questionset__questionnaire__id=int(qid))
    if ri.count() > 0: context[kind] = 'not-completed'

    # to invite
    if rh.count() == 0 and ri.count() == 0: context[kind] = 'to-invite'
    return ""
