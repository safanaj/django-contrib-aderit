from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_init, post_save, pre_save
from django.core.mail import EmailMessage
from models import *
from django.template import Context, Template
import logging, mimetypes, re

mailto_error = 'matteo.atti@aderit.it'
sender_error = 'error@sendmail.it'
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
    attachments = mail.attachments.all()
    if len(attachments) > 0:
	mail_attach = True
    else:
	mail_attach = False
    #kwargs.pop('type')
    #kwargs.pop('mailto')
    #txt = str(txt_body) % kwargs
    t = Template(txt_body)
    c = Context(kwargs)
    txt = t.render(c)
    try:
        tosend = EmailMessage(subj, txt, sender, 
		    [mailto])
        tosend.content_subtype = mail.content_subtype
        if mail_attach:
            for i in attachments:
                content_type = mimetypes.guess_type(i.attachment.path)[0]
		tosend.attach(i.attachment.name, i.attachment.read(), content_type)
	tosend.send()
        return True
    except Exception, e:
        txt = e
        EmailMessage(subj_error, txt, sender_error,
                    [mailto_error]).send()
        return False

