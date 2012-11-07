from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.template import Context, Template
import logging, re, mimetypes, os

logger = logging.getLogger("send_email_msg")

def send_email_msg(smtp_host='localhost', smtp_port=25, connection=None, smtp_user='',
                   smtp_passwd='', use_tls=False, backend=EmailBackend,
                   subject='', body='', from_email=None, headers=None, to=None, cc=None, bcc=None,
                   attachments=None, alternatives=None, encoding='utf-8',
                   send_it=True, in_bulk=False, custom_dict_string=None, chunk_size=None):
    """
    Wrapper function ... TOWRITE
    """
    if send_it:
        if not connection:
            smtp_cnx = backend(host=smtp_host, port=smtp_port,
                               username=smtp_user, password=smtp_passwd,
                               use_tls=use_tls)
        else:
            smtp_cnx = connection

    #alternatives deve essere una tupla contenente il mess alternativo html + il mimetype

    custom_dict = type_dict = None
    if custom_dict_string:
        try:
            custom_dict = eval(custom_dict_string)
        except Exception, e:
            logger.error("CustomDictString Exception: %s", e.message)
            #raise Exception("CustomDictString Error: %s" % e.message)

    if custom_dict:
        try:
            type_dict = custom_dict.pop('type_dict')
        except KeyError:
            raise Exception("Key type_dict is mandatory in custom_dict [bulk|single]")

        assert((type_dict == "bulk" and in_bulk == True) or
               (type_dict == "single" and in_bulk == False))

    messages = []

    if not isinstance(body, basestring) or not re.search('\w', body):
        raise Exception("Body is mandatory")

    if alternatives:
        for c,m in alternatives:
            if not isinstance(c, basestring) or not re.search('\w', c):
                raise Exception("Alternatives content is mandatory")
    elif alternatives is None:
        alternatives = []

    _attachments = []
    if attachments:
        for i in attachments:
            if isinstance(i, basestring) and os.path.isfile(i) and os.access(i, os.R_OK):
                ct, enc = mimetypes.guess_type(i)
                fn = os.path.basename(i)
                blob = open(i, 'rb').read()
                _attachments.append((fn,blob,ct))
            elif isinstance(i, tuple) and len(i) == 3:
                _attachments.append(i)
            else:
                logger.error("Attachments ignored: %s", i)
        attachments = _attachments

    if in_bulk:
        if type_dict:
            render_subj = Template(subject).render(Context(custom_dict))
            render_body = Template(body).render(Context(custom_dict))
            render_alternatives = []
            for c,m in alternatives:
                render_alternatives.append((Template(c).render(Context(custom_dict)),m))
        if chunk_size is not None and isinstance(chunk_size, int) and chunk_size > 2:
            dests = []
            while len(bcc) > 0:
                dests.append(bcc[:chunk_size])
                del bcc[:chunk_size]
            for bcc in dests:
                msg = EmailMultiAlternatives(subject=render_subj, body=render_body,
                                             from_email=from_email, headers=headers,
                                             to=[from_email], cc=None, bcc=bcc,
                                             attachments=attachments,
                                             alternatives=render_alternatives)
                msg.encoding = encoding
                msg.extra_headers.update({'Precedence':'bulk'})
                messages.append(msg)
        else:
            msg = EmailMultiAlternatives(subject=render_subj, body=render_body,
                                         from_email=from_email, headers=headers,
                                         to=[from_email], cc=None, bcc=bcc,
                                         attachments=attachments,
                                         alternatives=render_alternatives)
            msg.encoding = encoding
            msg.extra_headers.update({'Precedence':'bulk'})
            messages.append(msg)
    else:
        recipients = to or [] + cc or [] + bcc or []
        for r in recipients:
            render_subj = subject
            render_body = body
            if type_dict:
                render_subj = Template(subject).render(Context(custom_dict))
                render_body = Template(body).render(Context(custom_dict.get(r)))
                logger.debug("Template rendered: %s", render_body)
                render_alternatives = []
                for c,m in alternatives:
                    render_alternatives.append((Template(c).render(Context(custom_dict.get(r))),m))
                msg = EmailMultiAlternatives(subject=render_subj, body=render_body,
                                             from_email=from_email, headers=headers,
                                             to=[r], attachments=attachments,
                                             alternatives=render_alternatives)
                msg.encoding = encoding
                messages.append(msg)

    if not send_it:
        return messages
    else:
        return smtp_cnx.send_messages(messages)

