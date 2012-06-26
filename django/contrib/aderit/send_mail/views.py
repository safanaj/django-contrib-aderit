from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_init, post_save, pre_save
from django.core.mail import EmailMessage, EmailMultiAlternatives
from models import *
from django.template import Context, Template
import logging, mimetypes, re
import string
from django.contrib.aderit.send_mail.utils import send_email_msg


logger = logging.getLogger("django.debug")

mailto_error = 'matteo.atti@aderit.it'
sender_error = 'error@sendmail.it'
subj_error = 'SendMail Error'

def SendTypeMail(kwargs):
    """
    obbligatori: kwargs['type'], kwargs['mailto']
    """
    logger.info(kwargs)
    tipo = kwargs['type']
    try:
        mail = SendMail.objects.get(type_mail=tipo) 
    except SendMail.DoesNotExist:
        logger.error("Not found type")
        return False
    mailto = kwargs['mailto']
    body_txt = mail.body_txt
    body_html = mail.body_html
    if body_html:
        alternatives=[(body_html,'text/html')]
    else:
	alternatives=None
    subj = mail.subject
    sender = mail.mail_sender
    attachments = mail.attachments.all()
    if len(attachments) == 0:
	attachments = None
    else:
	logger.info(attachments)

    # build up a dict to template rendering
    conf_dict = {'type_dict':'single'}
    conf_dict.update(kwargs)
    conf_dict.pop('type')
    conf_dict.pop('mailto')
    # funzione che richiama utils.py e invoca send_email_msg con i parametri corretti
    logger.info(mailto)
    return send_email_msg(subject=subj,
                          from_email=sender,
                          body=body_txt,
                          to=mailto,
                          alternatives=alternatives,
                          attachments=[a.attachment.path for a in attachments],
                          custom_dict_string=str(conf_dict))


def SendTypeMailBulk(kwargs):
    """
    obbligatori: kwargs['type'], kwargs['mailto']
    """
    logger.info(kwargs)
    tipo = kwargs['type']
    try:
        mail = SendMail.objects.get(type_mail=tipo) 
    except SendMail.DoesNotExist:
        logger.error("Not found type")
        return False
    mailto = kwargs['mailto']
    body_txt = mail.body_txt
    body_html = mail.body_html
    if body_html:
        alternatives=[(body_html,'text/html')]
    else:
	alternatives=None
    subj = mail.subject
    sender = mail.mail_sender
    attachments = mail.attachments.all()
    if len(attachments) == 0:
	attachments = None
    else:
	logger.info(attachments)

    # build up a dict to template rendering
    conf_dict = {'type_dict':'bulk'}
    conf_dict.update(kwargs)
    conf_dict.pop('type')
    conf_dict.pop('mailto')
    # funzione che richiama utils.py e invoca send_email_msg con i parametri corretti
    logger.info(mailto)
    return send_email_msg(subject=subj,
                          from_email=sender,
                          body=body_txt,
                          bcc=mailto,
                          alternatives=alternatives,
                          attachments=[a.attachment.path for a in attachments],
                          in_bulk=True,
                          custom_dict_string=str(conf_dict))

