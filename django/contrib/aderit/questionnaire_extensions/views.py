# -*- coding: utf-8 -*-

# django.contrib.aderit.questionnaire_extensions.views -- python module
#
# Copyright (C) 2012 Aderit srl
#
# Author: Matteo Atti <matteo.atti@aderit.it>,
#                     <attuch@gmail.com>
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
Django Contrib Aderit Questionnaire Extensions views
'''
__copyright__ = '''Copyright (C) 2012 Aderit srl'''


from django.conf import settings
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy as reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.log import getLogger
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.html import conditional_escape
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.aderit.access_account import _get_model_from_auth_profile_module
from django.contrib.aderit.send_mail import SendTypeMail, SendTypeMailError
from django.contrib.aderit.generic_utils.views import \
    (GenericUtilView, GenericProtectedView)
from django.contrib.aderit.questionnaire_extensions.models import \
    (AccessAccount, Questionnaire, RunInfo, Answer, RunInfoHistory, QuestionSet, Question, Choice, Subject)
from django.contrib.aderit.questionnaire_extensions.forms import CSVQuestImporterForm
import re, random, os

logger = getLogger('aderit.questionnaire_extensions.views')

INVITATION_SEND_TYPE_MAIL = getattr(settings,
                                    'QEXT_INVITATION_SEND_MAIL_TYPENAME',
                                    'quest_invite')
REMINDER_SEND_TYPE_MAIL = getattr(settings, 'QEXT_REMINDER_SEND_MAIL_TYPENAME',
                                  'quest_remind')

class ShowReport(TemplateView, GenericUtilView):
    use_login_required_decorator = False
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        runinfo_id = int(kwargs['slug'])
        qid = RunInfo.objects.get(id=runinfo_id).questionset.questionnaire.id
        sid = RunInfo.objects.get(id=runinfo_id).subject.id
        answers = Answer.objects.filter(question__questionset__questionnaire__id=qid,
                                        subject__id=sid).order_by('question__number')
        answers = sorted(answers, key=lambda o: int(re.sub("[^0-9]",
                                                           "",
                                                           o.question.number)))
        this_runinfo = RunInfo.objects.get(subject__id=sid,
                                           questionset__questionnaire__id=qid)
        out = []
        for ans in answers:
            logger.debug(u"Q: %s - A: %s", ans.question, ans.answer)
            q_type = ans.question.type
            # if q_type not in ('choice', 'choice-freeform',
            #                    'choice-multiple', 'choice-multiple-freeform'):
            if ans.answer:
                anslist = eval(ans.answer)
            else:
                anslist = []
            if 'choice' not in q_type:
                # No choices to manage
                if len(anslist) > 0:
                    choiceval = anslist[0]
                else:
                    choiceval = ''
            else:
                if len(anslist) == 0:
                    choiceval = ''
                elif len(anslist) == 1:
                    # radio, single, yes-no
                    for anselt in anslist:
                        if q_type in ['choice-yesno','choice-yesnocomment','choice-yesnodontknow']:
                            choiceval = anselt
                        elif isinstance(anselt, list):
                            choiceval = anselt[0]
                        else:
                            choice = Choice.objects.get(question=ans.question,
                                                        value=anselt)
                            choiceval = choice.text
                else:  #mutiple, have to append text in string
                    choiceval = ''
                    #logger.debug("cycle over anslist: %s", anslist)
                    for anselt in anslist:
                        if isinstance(anselt, list):
                            # selected altro
                            choiceval += anselt[0] + '; '
                        else:
                            choice = Choice.objects.get(question=ans.question,
                                                        value=anselt)
                            choiceval += choice.text + '; '
            logger.debug(u"Q: %s - A: %s -- val: %s", ans.question, ans.answer, choiceval)
            new_url = reverse('questionset', args=[this_runinfo.runid,
                                                   ans.question.questionset.sortid])
            logger.debug(new_url)
            out.append({'q_numb' : ans.question.number,
                        'q_url' : new_url,
                        'q_head' : ans.question.questionset.heading,
                        'q_text' : ans.question.text,
                        'q_answ' : unicode(choiceval),
                        })
        kwargs.update({
                'out' : out,
                'q_runinfo' : this_runinfo
                })
        return kwargs




class ExportCsv(GenericProtectedView):
    slug = None
    slug_field = 'id'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ExportCsv, self).dispatch(request, *args, **kwargs)

    def _csv_response(self, answers):
        import tempfile, csv
        from django.core.servers.basehttp import FileWrapper
        fd = tempfile.TemporaryFile()
        writer = csv.DictWriter(fd, ['domanda', 'valore'])
        writer.writerow({u'domanda' : u"Question", u'valore' : u"Answer"})
        for ans in answers:
            try:
                choice = Choice.objects.get(question=ans.question, value=ans.answer)
                choiceval = eval(unicode(choice.text))[0]
            except Exception, e:
                choiceval = ""
                choicevallist = ans.answer
                try:
                    if len(eval(choicevallist)) > 1:
                        for i in eval(choicevallist):
                            if type(i) == list:
                                choiceval += i[0] + ";"
                            else:
                                choiceval += i + ";"
                    else:
                        try:
                            choicevalue = eval(choicevallist)[0]
                            if type(choicevalue) == list:
                                choiceval = choicevalue[0]
                            else:
                                choiceval = choicevalue
                        except:
                            choiceval = ""
                except:
                    choiceval = ""
                if not isinstance(choiceval, basestring):
                    choiceval = unicode(choiceval)
                writer.writerow({
                        u'domanda' : ans.question.number.encode("utf-8") + ") " + ans.question.questionset.heading.encode("utf-8") + ": " + ans.question.text.encode("utf-8"),
                        u'valore' : choiceval.encode("utf-8")})
        response = HttpResponse(FileWrapper(fd), mimetype="text/csv")
        response['Content-Length'] = fd.tell()
        response['Content-Disposition'] = 'attachment; filename="export-%s.csv"' % self.qid
        fd.seek(0)
        # fd.close() # Non chiudere questo file temp perchè altrimenti la response è vuota
        return response


    def get(self, request, *args, **kwargs):
        self.qid = int(kwargs.get('slug', 0))
        sid = int(kwargs.get('subjid', 0))
        kw = { 'question__questionset__questionnaire__id' : self.qid }
        if sid != 0:
            kw.update({'subject__id' : sid })
        answers = Answer.objects.filter(**kw).order_by('question__id')
        answers = sorted(answers, key=lambda o: int(re.sub("[^0-9]", "", o.question.number)))
        response = self._csv_response(answers)
        return response


class SendInvitation(GenericProtectedView):
    slug = None
    slug_field = 'id'
    account_model = _get_model_from_auth_profile_module()

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SendInvitation, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        qid = int(kwargs.get('slug', 0))
        subjid = kwargs.get('subjid', None)
        if not subjid:
            _subjects = self.account_model.objects.filter(questionnaires__id=qid)
            subjects = [i.subject for i in _subjects if i.subject is not None and i.subject.state == "active"]
        else:
            subjects = Subject.objects.filter(id=int(subjid),
                                              state="active")
        for i in subjects:
            runinfo = RunInfo.objects.filter(subject=i,
                                             questionset__questionnaire__id=qid)
            runinfohistory = RunInfoHistory.objects.filter(subject=i,
                                                           questionnaire__id=qid)
            if runinfo.count() == 0 and runinfohistory.count() == 0:
                logger.debug("il soggetto %s deve ancora compilare il questionario %s: creare il runinfo associato", i.givenname, qid)
                randomstr = str(''.join(random.sample('abcdefghilmnopqrstuvz0123456789', 10)))
                new_run = RunInfo(subject=i,
                                  random=randomstr,
                                  runid=randomstr,
                                  questionset=QuestionSet.objects.filter(questionnaire__id=qid).order_by('sortid')[0])
                new_run.save()
                logger.debug("creato per %s",  i.givenname)
                link = Site.objects.get_current().domain + unicode(reverse('questionnaire', args=[randomstr] ))
                kwargs = {'type': INVITATION_SEND_TYPE_MAIL,
                          'mailto': [i.email],
                          i.email : {'user': i.givenname,
                                     'link': link }
                          }
                try:
                    SendTypeMail(kwargs)
                except SendTypeMailError, e:
                    logger.error("In SendInvitation invitation Exc: ", e)
            elif runinfo.count() > 0 and runinfohistory.count() == 0:
                logger.debug("il soggetto %s deve finire di compilare il questionario %s: inviare il runid associato", i.givenname, qid)
                link = Site.objects.get_current().domain + unicode(reverse('questionnaire',  args=[runinfo[0].runid] ))
                kwargs = {'type': REMINDER_SEND_TYPE_MAIL,
                          'mailto': [i.email],
                          i.email : {'user': i.givenname,
                                     'link': link}
                          }
                try:
                    SendTypeMail(kwargs)
                except SendTypeMailError, e:
                    logger.error("In SendInvitation reminder Exc: ", e)
            elif runinfo.count() == 0 and runinfohistory.count() > 0:
                logger.debug("il soggetto %s ha gia' concluso il questionario %s: non inviare nulla", i.givenname, qid)
            else:
                logger.error("Situazione non corretta per subject %s", i.givenname)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class ShowGraph(TemplateView, GenericProtectedView):
    slug = None
    slug_field = 'id'
    template_name = 'questionnaire/quest_graph.html'
    account_model = _get_model_from_auth_profile_module()

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShowGraph, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        qid = int(kwargs['slug'])
        _subjects = self.account_model.objects.filter(questionnaires__id=qid)
        subjects = [i.subject for i in _subjects if i.subject is not None and i.subject.state == "active"]
        quest_comp = RunInfoHistory.objects.filter(questionnaire__id=qid)
        comp = quest_comp.count()
        quest_started = RunInfo.objects.filter(questionset__questionnaire__id=qid)
        not_comp = quest_started.count()
        not_invited = len(subjects) - comp - not_comp
        if not_invited < 0: not_invited = 0
        questions = Question.objects.filter(questionset__questionnaire=qid)
        questions = sorted(questions, key=lambda o: int(re.sub("[^0-9]",
                                                               "",
                                                               str(o.number))))
        lista = []
        lista_percent = []
        for i in questions:
            newdiz = {}
            newdiz_percent = {}
            q_type = i.type
            answers = Answer.objects.filter(question=i)
            out = []
            for ans in answers:
                # logger.debug(u"Q: %s - A: %s", ans.question, ans.answer)
                q_type = ans.question.type
                if ans.answer:
                    anslist = eval(ans.answer)
                else:
                    anslist = []
                if 'choice' not in q_type:
                    # No choices to manage
                    if len(anslist) > 0:
                        choiceval = anslist[0]
                    else:
                        choiceval = ''

                    if not newdiz.get('Open Answer'):
                        newdiz['Open Answer'] = 1
                    else:
                        newdiz['Open Answer'] += 1
                else:
                    if len(anslist) == 0:
                        choiceval = ''
                    elif len(anslist) == 1:
                        # radio, single, yes-no
                        for anselt in anslist:
                            if q_type in ['choice-yesno','choice-yesnocomment','choice-yesnodontknow']:
                                choiceval = anselt

                                if not newdiz.get(anselt, None):
                                    newdiz[conditional_escape(anselt)] = 1
                                else:
                                    newdiz[conditional_escape(anselt)] += 1

                            elif isinstance(anselt, list):
                                choiceval = anselt[0]

                                if not newdiz.get('Open Answer', None):
                                    newdiz['Open Answer'] = 1
                                else:
                                    newdiz['Open Answer'] += 1
                            else:
                                choice = Choice.objects.get(question=ans.question,
                                                            value=anselt)
                                choiceval = choice.value

                                if not newdiz.get(choice.value, None):
                                    newdiz[conditional_escape(choice.value)] = 1
                                else:
                                    newdiz[conditional_escape(choice.value)] += 1

                    else:  #mutiple, have to append text in string
                        choiceval = ''
                        for anselt in anslist:
                            if isinstance(anselt, list):
                                # selected altro
                                choiceval = anselt[0]

                                if not newdiz.get('Open Answer', None):
                                    newdiz['Open Answer'] = 1
                                else:
                                    newdiz['Open Answer'] += 1
                            else:
                                choice = Choice.objects.get(question=ans.question,
                                                            value=anselt)
                                choiceval = choice.value

                                if not newdiz.get(choiceval, None):
                                    newdiz[conditional_escape(choiceval)] = 1
                                else:
                                    newdiz[conditional_escape(choiceval)] += 1

            lista_title = conditional_escape(str(i.number) + ") " + i.text)
            lista.append((lista_title, newdiz, i.number))
            for y in newdiz.items():
                if y[1]:
                    newdiz_percent[y[0]] = round(float(y[1])/float(len(subjects))*100,
                                                 2)
            lista_percent.append((lista_title, newdiz_percent, i.number))
        return TemplateResponse(self.request, self.template_name, locals())

class CSVQuestImporterView(FormView, GenericProtectedView):
    ''' Take a csv file and represent it into an editable table in template 
    '''

    form_class = CSVQuestImporterForm
    template_name = 'questionnaire_extensions/csvimporter.html'

    def form_valid(self, form):
        data = self.request.FILES['csv_import']
        path = default_storage.save('csv_importers/%s' % data,
                                    ContentFile(data.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        f = open(tmp_file)
        content_file = []
        heading_file = ""
        n = 0
        for line in f:
            n += 1
            if n == 1:
                heading_file = line.split('","')
            else:
                x = line.split('","')
                diz = {}
                for n,f in enumerate(x):
                    diz.update({ heading_file[n].replace('\n','').replace('\r','').replace('"','') : f.replace('\n','').replace('\r','').replace('"','') })
                content_file.append(diz)
        os.remove(tmp_file)
        quests = Questionnaire.objects.all()
        return TemplateResponse(self.request, self.template_name, locals())

class CSVQuestImporterAddView(GenericProtectedView):
    ''' Take a table for confirm the importing, showing and managing errors 
    '''

    template_name = 'questionnaire_extensions/csvimporter.html'

    def post(self, request, *args, **kwargs):
        i = 1
        len_record = int(request.POST.get('len_record', 0))
        quests = request.POST.getlist('quests_selected', [])
        elements = []
        content_file = []
        content_added = []
        while i <= len_record:
            diz = {}
            for y in request.POST.keys():
                match = re.match(r'(.*)_(\d+)', y)
                if match and match.groups()[1] == '%s' % str(i):
                    diz.update({ match.groups()[0] : request.POST.get(y,'') })
            if diz: elements.append(diz)
            i += 1
        for user_dict in elements:
            if 'email' not in user_dict.keys() or \
                   'first_name' not in user_dict.keys() or \
                   'last_name' not in user_dict.keys() or \
                   'password' not in user_dict.keys():
                user_dict = ({ 'Error' : _('Formattazione campi sbagliata: modifica file CSV') })
                content_file.append(user_dict)
                continue
            if not user_dict['email']:
                user_dict.update({ 'Error' : _('Campo Mail obbligatorio') })
                content_file.append(user_dict)
                continue
            elif User.objects.filter(username=user_dict['email']).exists() or \
                     User.objects.filter(email=user_dict['email']).exists():
                user_dict.update({ 'Error' : _("Mail gia' esistente") })
                content_file.append(user_dict)
                continue
            else:
                if user_dict['password']:
                    psw = user_dict['password']
                else:
                    psw = user_dict['email']
                kw = { 'username' : user_dict['email'],
                       'email' : user_dict['email'],
                       'first_name' : user_dict['first_name'],
                       'last_name' : user_dict['last_name']
                       }
                new_user = User.objects.create(**kw)
                new_user.set_password(psw)
                new_user.save()
                set_qid = new_user.get_profile()
                set_qid.questionnaires = [int(x) for x in quests]
                user_dict.update({ 'password' : psw })
                content_added.append(user_dict)
                continue
        q_added = Questionnaire.objects.filter(id__in=quests)
        old_quests = [int(x) for x in quests]
        quests = Questionnaire.objects.all()
        return TemplateResponse(self.request, self.template_name, locals())
