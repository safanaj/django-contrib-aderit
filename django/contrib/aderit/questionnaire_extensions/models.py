# django.contrib.aderit.questionnaire_extensions.models -- python module
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
Seantis Questionnaire models extensions by Aderit.
'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''

try:
    from questionnaire.models import Subject as SQSubject
    from questionnaire.models import QuestionSet as SQQuestionSet
    from django.contrib.aderit.questionnaire_extensions import \
        (Questionnaire, Question, Answer,
         RunInfo, RunInfoHistory, Choice)
except ImportError:
    pass
else:
    class Subject(SQSubject):
        class Meta:
            proxy = True

    class QuestionSet(SQQuestionSet):
        class Meta:
            proxy = True

