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

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_save, post_save
from django.db.models import fields as models_fields
from django.utils.log import getLogger

logger = getLogger('aderit.questionnaire_extensions.models')

try:
    from questionnaire.models import Subject
    from questionnaire.models import QuestionSet as SQQuestionSet
    from questionnaire.models import (Questionnaire, Question, Answer,
                                      RunInfo, RunInfoHistory, Choice)
    from questionnaire.views import questionset_satisfies_checks

except ImportError:
    raise ImproperlyConfigured('Questionnaire_Extensions by Aderit '
                               'depends strictly on seantis questionnaire')

try:
    from django.contrib.aderit.access_account.models import \
        (AccessAccount as _AccessAccount, User)
    from django.contrib.aderit.access_account import \
        _get_model_from_auth_profile_module
except ImportError:
    raise ImproperlyConfigured('Questionnaire_Extensions by Aderit '
                               'needs AccessAccount for extends it with Subjects')

class AccessAccount(_AccessAccount):
    subject = models_fields.related.OneToOneField(Subject, blank=True, null=True)
    questionnaires = models_fields.related.ManyToManyField(Questionnaire,
                                                           blank=True, null=True)

    class Meta:
        abstract = True

class QuestionSet(SQQuestionSet):
    class Meta:
        proxy = True

    def previous(self, runinfo=None):
        if runinfo is None:
            return self.prev()

        previous = self.prev()
        while previous and not questionset_satisfies_checks(previous, runinfo):
            if previous.prev():
                previous = previous.prev()
            else:
                logger.critical("No valid previous QusetionSet "
                                "found: RI: %s - QS: %s",
                                runinfo, runinfo.questionset.sortid)
                break
        return previous


def create_subject_account(sender, instance, created, **kwargs):
    '''
    @sender: Account model
    @instance: account Account model instance
    '''
    # TODO: valuate and make it configurable via settings
    if isinstance(instance, User):
        try:
            account = instance.get_profile()
        except:
            return
    elif isinstance(instance, _get_model_from_auth_profile_module()):
        account = instance
    else:
        logger.error("create_subject_account signal: sender: %s - instance: %s",
                     sender, instance)
        return

    if created:
        subject, created_subj = Subject.objects.get_or_create(state='active',
                                                          surname=account.username,
                                                          givenname=account.fullname,
                                                          email=account.email)
        if created_subj:
            account.subject = subject
            account.save()
    else:
        subject = account.subject
        if subject is None:
            account.subject, created_subj = Subject.objects.get_or_create(state='active',
                                                                           surname=account.username,
                                                                           givenname=account.fullname,
                                                                           email=account.email)
            account.subject.save()
            account.save()
            return
        if account.is_active:
            subject.state = 'active'
        else:
            subject.state = 'inactive'
        subject.surname = account.username
        subject.givenname = account.fullname
        subject.email = account.email
        subject.save()


# TODO: Fix and do in better way!
post_save.connect(create_subject_account,
                  sender=_get_model_from_auth_profile_module())
