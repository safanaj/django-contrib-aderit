# -*- coding: utf-8 -*-
from django.conf import settings
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy as reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.log import getLogger
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.sites.models import Site
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.aderit.access_account import _get_model_from_auth_profile_module
from django.contrib.aderit.send_mail import SendTypeMail, SendTypeMailError
from django.contrib.aderit.generic_utils.views import \
    (GenericUtilView, GenericProtectedView)
from django.contrib.aderit.questionnaire_extensions.models import \
    (RunInfo, Answer, RunInfoHistory, QuestionSet)
import re, random

logger = getLogger('aderit.questionnaire_extensions.views')

INVITATION_SEND_TYPE_MAIL = getattr(settings,
                                    'QEXT_INVITATION_SEND_MAIL_TYPENAME',
                                    'quest_invite')
REMINDER_SEND_TYPE_MAIL = getattr(settings, 'QEXT_REMINDER_SEND_MAIL_TYPENAME',
                                  'quest_remind')

class ShowReport(TemplateView, GenericUtilView):
    use_login_required_decorator = True
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
            try:
                choice = Choice.objects.get(question=ans.question,
                                            value=ans.answer)
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
            new_url = reverse('questionset', args=[this_runinfo.runid,
                                                   ans.question.questionset.sortid])
            logger.debug(new_url)
            out.append({'q_numb' : ans.question.number,
                        'q_url' : new_url,
                        'q_head' : ans.question.questionset.heading,
                        'q_text' : ans.question.text,
                        'q_answ' : str(choiceval),
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
        qid = int(kwargs['slug'])
        _subjects = self.account_model.objects.filter(questionnaires__id=qid)
        subjects = [i.subject for i in _subjects if i.subject is not None and i.subject.state == "active"]
        # non_auth_subjects = [s for s in Subjects.objects.exclude(id__in=[i.id for i in subjects]) if s.email]
        logger.debug(subjects)
        # logger.debug(non_auth_subjects)
        for i in subjects:
            runinfo = RunInfo.objects.filter(subject=i,
                                             questionset__questionnaire__id=qid
                                             )
            runinfohistory = RunInfoHistory.objects.filter(subject=i,
                                                           questionnaire__id=qid
                                                           )
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
