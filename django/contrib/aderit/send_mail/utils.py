from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.template import Context, Template
import logging, re, mimetypes

logger = logging.getLogger("django.debug")

def send_email_msg(smtp_host='localhost', smtp_port='25', connection=None, smtp_user='', smtp_passwd='', use_tls=False,
		   subject='', body='', from_email=None, headers=None, to=None, cc=None, bcc=None, attachments=None, alternatives=None, encoding='utf-8',
		   send_it=True, in_bulk=False, custom_dict_string=None):
    """
    Wrapper function ... TOWRITE
    """
    if not connection:
        smtp_cnx = EmailBackend(host=smtp_host, port=smtp_port, username=smtp_user, password=smtp_passwd, use_tls=use_tls)
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
        
        assert(type_dict == "bulk" and in_bulk == True)
	assert(type_dict == "single" and in_bulk == False)
    
    messages = []    

    if not isinstance(body, basestring) or not re.search('\w', body):
	raise Exception("Body is mandatory")

    if alternatives:
        for c,m in alternatives:
            if not isinstance(c, basestring) or not re.search('\w', c):
	        raise Exception("Alternatives content is mandatory")
	
    if in_bulk:
	if type_dict:
	    body = Template(body).render(Context(custom_dict))
	    render_alternatives = []
	    for c,m in alternatives:
	        render_alternatives.append((Template(c).render(Context(custom_dict)),m))
        msg = EmailMultiAlternatives(subject=subject, body=body, from_email=from_email, headers=headers, to=to, cc=cc, bcc=bcc, attachments=attachments, alternatives=render_alternatives)
        msg.encoding = encoding
	msg.extra_headers.update({'Precedence':'bulk'})
	messages.append(msg)
    else:
	recipients = to or [] + cc or [] + bcc or []
	for r in recipients:
 	    render_body = body
 	    render_alternatives = alternatives
	    if type_dict:
	        render_body = Template(body).render(Context(custom_dict.get(r)))
		render_alternatives = []
	 	for c,m in alternatives:
		    render_alternatives.append((Template(c).render(Context(custom_dict.get(r))),m))
            msg = EmailMultiAlternatives(subject=subject, body=render_body, from_email=from_email, headers=headers, to=[r], attachments=attachments, alternatives=render_alternatives)
            msg.encoding = encoding
	    messages.append(msg)

    if not send_it:
	return messages
    else:
	lenmess = 0
	for msg in messages:
	    if attachments:
	        for i in attachments:
		    logger.info(i.attachment.name)
		    logger.info(i.attachment.path)
                    #content_type = mimetypes.guess_type(i.attachment.path)[0]
                    #msg.attach(i.attachment.name, i.attachment.read(), content_type)
                    msg.attach_file(i.attachment.path)
	    lenmess += msg.send() 
        return lenmess

