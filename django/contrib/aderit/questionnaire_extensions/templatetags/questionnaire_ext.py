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
