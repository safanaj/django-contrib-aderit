# django.contrib.aderit.questionnaire_extensions -- python module
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
Seantis Questionnaire extensions by Aderit.
'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''

from django.conf import settings

if 'questionnaire' in settings.INSTALLED_APPS:
    #from questionnaire.models import Subject as SQSubject
    #from questionnaire.models import QuestionSet as SQQuestionSet
    from questionnaire.models import (Questionnaire, Question, Answer,
                                      RunInfo, RunInfoHistory, Choice)
    from django.contrib.aderit.questionnaire_extensions.models import Subject
    from django.contrib.aderit.questionnaire_extensions.models import QuestionSet
