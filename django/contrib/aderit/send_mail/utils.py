# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# pylint: disable-msg=C0103,R0912,R0913,R0914,R0915,W0703

# utils.py -- utility, shold not depend on a django project env
#
# Copyright (C) 2012 Aderit srl
#
# Author: Marco Bardelli <marco.bardelli@aderit.it>, <bardelli.marco@gmail.com>
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

'''Sending mails utility functions.'''

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.template import Context, Template
import logging
import re
import mimetypes
import os

logger = logging.getLogger("send_email_msg")


def send_email_msg(smtp_host='localhost', smtp_port=25, connection=None,
                   smtp_user='', smtp_passwd='', use_tls=False,
                   backend=EmailBackend, subject='', body='',
                   from_email=None, headers=None, to=None, cc=None, bcc=None,
                   attachments=None, alternatives=None, encoding='utf-8',
                   send_it=True, in_bulk=False, chunk_size=None,
                   custom_dict_string=None, custom_dict=None):
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

    # alternatives deve essere una tupla contenente il mess
    # alternativo html + il mimetype

    type_dict = None
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
            raise Exception("Key type_dict is mandatory in "
                            "custom_dict [bulk|single]")

        assert((type_dict == "bulk" and in_bulk is True) or
               (type_dict == "single" and in_bulk is False))

    messages = []

    if not isinstance(body, basestring) or not re.search(r'\w', body):
        raise Exception("Body is mandatory")

    if alternatives:
        for c, m in alternatives:
            if not isinstance(c, basestring) or not re.search(r'\w', c):
                raise Exception("Alternatives content is mandatory")
    elif alternatives is None:
        alternatives = []

    _attachments = []
    if attachments:
        for i in attachments:
            if isinstance(i, basestring) and os.path.isfile(i) and \
                    os.access(i, os.R_OK):
                ct = mimetypes.guess_type(i)[0]
                fn = os.path.basename(i)
                blob = open(i, 'rb').read()
                _attachments.append((fn, blob, ct))
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
            for c, m in alternatives:
                _rendered = Template(c).render(Context(custom_dict))
                render_alternatives.append((_rendered, m))
        if chunk_size is not None and \
                isinstance(chunk_size, int) and \
                chunk_size > 2:
            dests = []
            if bcc is None:
                bcc = []
            while len(bcc) > 0:
                dests.append(bcc[:chunk_size])
                del bcc[:chunk_size]
            for _bcc in dests:
                msg = EmailMultiAlternatives(subject=render_subj,
                                             body=render_body,
                                             from_email=from_email,
                                             headers=headers,
                                             to=[from_email], cc=None,
                                             bcc=_bcc,
                                             attachments=attachments,
                                             alternatives=render_alternatives)
                msg.encoding = encoding
                msg.extra_headers.update({'Precedence': 'bulk'})
                messages.append(msg)
        else:
            msg = EmailMultiAlternatives(subject=render_subj, body=render_body,
                                         from_email=from_email,
                                         headers=headers,
                                         to=[from_email], cc=None, bcc=bcc,
                                         attachments=attachments,
                                         alternatives=render_alternatives)
            msg.encoding = encoding
            msg.extra_headers.update({'Precedence': 'bulk'})
            messages.append(msg)
    else:
        recipients = to or [] + cc or [] + bcc or []
        for r in recipients:
            render_subj = subject
            render_body = body
            if type_dict:
                render_subj = Template(subject).render(Context(custom_dict))
                ctx_r = custom_dict.get(r)
                render_body = Template(body).render(Context(ctx_r))
                logger.debug("Template rendered: %s", render_body)
                render_alternatives = []
                for c, m in alternatives:
                    _rendered = Template(c).render(Context(custom_dict.get(r)))
                    render_alternatives.append((_rendered, m))
                msg = EmailMultiAlternatives(subject=render_subj,
                                             body=render_body,
                                             from_email=from_email,
                                             headers=headers,
                                             to=[r], attachments=attachments,
                                             alternatives=render_alternatives)
                msg.encoding = encoding
                messages.append(msg)

    if not send_it:
        return messages
    else:
        return smtp_cnx.send_messages(messages)
