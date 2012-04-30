from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_init, post_save, pre_save
from django.core.mail import EmailMessage
from models import *
import logging

mailto_error = 'matteo.atti@aderit.it'
sender_error = 'error@amail.it'
subj_error = 'SendMail Error'

def SendTypeMail(kwargs):
    """
    obbligatori: kwargs['type'], kwargs['mailto']
    """
    logging.error(kwargs)
    tipo = kwargs['type']
    try:
        mail = SendMail.objects.get(type_mail=tipo) 
    except SendMail.DoesNotExist:
        logging.error("Not found type")
        return False
    mailto = kwargs['mailto']
    txt_body = mail.body
    subj = mail.subject
    sender = mail.mail_sender
    kwargs.pop('type')
    kwargs.pop('mailto')
    txt = str(txt_body) % kwargs
    #logging.error(txt)
    try:
        EmailMessage(subj, txt, sender, 
		    [mailto]).send()
        return True
    except Exception, e:
        txt = e
        EmailMessage(subj_error, txt, sender_error,
                    [mailto_error]).send()
        return False

