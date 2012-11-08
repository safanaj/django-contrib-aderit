from django.db import models
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.backends.base import BaseEmailBackend
from django.template import Context, Template
from django.utils.log import getLogger
from django.contrib.aderit.send_mail.utils import send_email_msg
from django.contrib.aderit.send_mail.models import SendMail

logger = getLogger("aderit.send_mail")

mailto_error = getattr(settings, 'ADERIT_SEND_MAIL_ERROR_MAILTO', 'matteo.atti@aderit.it')
sender_error = getattr(settings, 'ADERIT_SEND_MAIL_ERROR_SENDER', 'error@sendmail.it')
subj_error = getattr(settings, 'ADERIT_SEND_MAIL_ERROR_SUBJ', 'aderit.SendMail Error')



def _SendTypeMail(kwargs, in_bulk=False):
    """
    il dizionario kwargs prevede due khiavi obbligatorie: 'type' e 'mailto'
    'type'   : deve essere il valore della chiave `type_mail' nel modello SendMail
    'mailto' : deve essere la LISTA dei destinatari

    Il dizionario @kwargs è del tipo:
    {
      'type': 'stringa',                                               -- OBBLIGATORIO
      'mailto': [lista],                                               -- OBBLIGATORIO
      'smtp_connection': <oggetto EmailBackend> o None,                -- OPZIONALE
      'smtp_host': 'stringa',                                          -- OPZIONALE
      'smtp_port': <int>,                                              -- OPZIONALE
      'smtp_user': 'stringa',                                          -- OPZIONALE
      'smtp_password': 'stringa',                                      -- OPZIONALE
      'smtp_use_tls': <bool>,                                          -- OPZIONALE
      'email_backend': <sottoclasse di BaseEmailBackend> o 'stringa',  -- OPZIONALE

      #### per i contesti con qui rendere i templates
      #### NB: dovrebbero essere lo stesso numero degli elementi in 'mailto'
      '<email, presente in [mailto]>1': { <CONTESTO DA RENDERE> },
      '<email, presente in [mailto]>2': { <CONTESTO DA RENDERE> },
      ...
      '<email, presente in [mailto]>N': { <CONTESTO DA RENDERE> },
    }

    @in_bulk: tipo di invio, True o False
    """
    logger.debug("_SendTypeMail (in_bulk=%s) kw: %s", in_bulk, kwargs)
    try:
        tipo = kwargs['type']
    except KeyError:
        raise KeyError("type key is required to query SendMail Model")
    try:
        mailto = kwargs['mailto']
    except KeyError:
        raise KeyError("mailto key is required to send an email")
    try:
        mail = SendMail.objects.get(type_mail=tipo)
    except SendMail.DoesNotExist:
        raise SendMail.DoesNotExist("requested SendMail type: \"%s\" does not exist" % tipo)
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
        attachments = []
    else:
        logger.debug("attachments: %s", attachments)

    # build up a dict to template rendering
    if in_bulk:
        conf_dict = {'type_dict':'bulk'}
    else:
        conf_dict = {'type_dict':'single'}
    conf_dict.update(kwargs)
    conf_dict.pop('type')
    conf_dict.pop('mailto')
    connection = conf_dict.pop('smtp_conection', None)
    smtp_host = conf_dict.pop('smtp_host', getattr(settings, 'EMAIL_HOST', 'localhost'))
    smtp_port = conf_dict.pop('smtp_port', getattr(settings, 'EMAIL_PORT', 25))
    smtp_user = conf_dict.pop('smtp_user', getattr(settings, 'EMAIL_HOST_USER', ''))
    smtp_password = conf_dict.pop('smtp_password', getattr(settings, 'EMAIL_HOST_PASSWORD', ''))
    smtp_use_tls = conf_dict.pop('smtp_use_tls', getattr(settings, 'EMAIL_USE_TLS', False))
    email_backend = conf_dict.pop('email_backend', getattr(settings, 'EMAIL_BACKEND', EmailBackend))
    if isinstance(email_backend, str):
        from django.utils.importlib import import_module
        mod_name = '.'.join(email_backend.split('.')[:-1])
        class_name = email_backend.split('.')[-1]
        try:
            mod = import_module(mod_name)
        except ValueError:
            raise ValueError("Invalid module name in email_backend key: %s" % mod_name)
        except ImportError:
            raise ImportError("No module named %s" % mod_name)
        try:
            email_backend = getattr(mod, class_name)
        except AttributeError:
            raise AttributeError("No class % in %s module" % (class_name, mod_name))
    if not issubclass(email_backend, BaseEmailBackend):
        raise Exception("email_backend have to be a subclass BaseEmailBackend")
    logger.debug("Send mail %s to %s -- conf_dict_string: %s", subj, mailto, str(conf_dict))
    try:
        return send_email_msg(smtp_host=smtp_host,
                              smtp_port=smtp_port,
                              connection=connection,
                              smtp_user=smtp_user,
                              smtp_passwd=smtp_password,
                              use_tls=smtp_use_tls,
                              backend=email_backend,
                              subject=subj,
                              from_email=sender,
                              body=body_txt,
                              to=mailto,
                              alternatives=alternatives,
                              attachments=[a.attachment.path for a in attachments],
                              custom_dict=conf_dict)
    except Exception, e:
        logger.critical("SendTypeMail: send_mail_msg fail: %s", e)
        # send an email to mailto_error ...
        raise e




def SendTypeMail(kwargs):
    """
    obbligatori: kwargs['type'], kwargs['mailto']

    vedi doc di _SendTypeMail
    """
    return _SendTypeMail(kwargs, in_bulk=False)


def SendTypeMailBulk(kwargs):
    """
    obbligatori: kwargs['type'], kwargs['mailto']

    vedi doc di _SendTypeMail
    """
    return _SendTypeMail(kwargs, in_bulk=True)
