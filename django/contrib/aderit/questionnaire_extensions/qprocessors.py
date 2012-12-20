# django.contrib.aderit.questionnaire_extensions.models -- python module
#
# Copyright (C) 2012 Aderit srl
#
# Authors: Marco Bardelli <marco.bardelli@aderit.it>,
#                        <bardelli.marco@gmail.com>,
#          Matteo Atti <matteo.atti@aderit.it>,
#                      <attuch@gmail.com>
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
Extensions of qprocessors.py for adding new type of questions
'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''
from django.utils.log import getLogger
from django.utils.simplejson import dumps
from django.utils.translation import ugettext as _, ungettext

from questionnaire import (question_proc, answer_proc, add_type,
                           AnswerException)

logger = getLogger('aderit.questionnaire_extensions.qprocessors')

@question_proc('choice-select')
def question_choice(request, question):
    choices = []
    jstriggers = []

    cd = question.getcheckdict()
    key = "question_%s" % question.number
    key2 = "question_%s_comment" % question.number
    val = None
    if key in request.POST:
        val = request.POST[key]
    else:
        if 'default' in cd:
            val = cd['default']
    # maybe only for initial
    for choice in question.choices():
        choices.append( ( choice.value == val, choice, ) )

    return {
        'choices'   : choices,
        'sel_entry' : val == '_entry_',
        'qvalue'    : val or '',
        'required'  : True,
        'comment'   : request.POST.get(key2, ""),
        'jstriggers': jstriggers,
    }

@answer_proc('choice-select')
def process_choice(question, answer):
    opt = answer['ANSWER'] or ''
    if not opt:
        raise AnswerException(_(u'You must select an option'))
    valid = [c.value for c in question.choices()]
    if opt not in valid:
        raise AnswerException(_(u'Invalid option!'))
    return dumps([opt])
add_type('choice-select', 'Choice [select]')


@question_proc('date-select')
def question_date(request, question):
    key = "question_%s" % question.number
    value = question.getcheckdict().get('default','')
    if key in request.POST:
        value = request.POST[key]
    return {
        'required' : question.getcheckdict().get('required', False),
        'value' : value,
    }

@answer_proc('date-select')
def process_date(question, answer):
    checkdict = question.getcheckdict()
    ans = answer['ANSWER'] or ''
    if ans:
        return dumps([ans])
    return dumps([])
add_type('date-select', 'Date [select]')
