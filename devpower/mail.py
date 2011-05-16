# coding: utf-8
#
# Copyright (C) 2011 by Edgar Merino (http://devio.us/~emerino)
#
# Licensed under the Artistic License 2.0 (The License). 
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#    http://www.perlfoundation.org/artistic_license_2_0
#
# THE PACKAGE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS
# IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES. THE IMPLIED
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
# NON-INFRINGEMENT ARE DISCLAIMED TO THE EXTENT PERMITTED BY YOUR LOCAL
# LAW. UNLESS REQUIRED BY LAW, NO COPYRIGHT HOLDER OR CONTRIBUTOR WILL
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
# DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THE PACKAGE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# Requerimientos: python >= 2.5

import os
import re
import smtplib

from email import Charset
from email.parser import Parser
from email.header import Header, decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Iterators import typed_subpart_iterator
from email.generator import Generator
from cStringIO import StringIO
from subprocess import Popen, PIPE

class UnicodeParser(Parser):
    """
    Esta clase devuelve las cabeceras de un correo
    electrónico como cadenas unicode.
    """

    def __init__(self):
        Parser.__init__(self)

    def parse(self, fp, headersonly=False):
        data = Parser.parse(self, fp, headersonly)
        orig_data = {}
    
        for key, value in data.items():
            orig_data[key.lower()] = value

        def get_unicode_header(header):
            return unicode_header(orig_data[header.lower()])

        data.__getitem__ = get_unicode_header

        return data

def unicode_header(header):
    decoded_header = decode_header(header)
    header = ""

    for part in decoded_header:
        if part[1]:
            header += unicode(part[0], part[1])
        else:
            header += part[0]

        header += " "

    return header

def extract_address(address_header):
    address = address_header

    if address_header.find("<") != -1:
        address = re.split("<|>", address_header)[1]

    return address.lower().lstrip().rstrip()

def unicode_email_body(email):
    body = ""

    if email.is_multipart():
        for part in typed_subpart_iterator(email, "text", "plain"):
            charset = part.get_content_charset()

            # Si no se especificó un encoding intentamos con iso-8859-1
            if not charset:
                charset = "iso-8859-1"

            body += unicode(part.get_payload(decode=True), charset)
    else:
        charset = email.get_content_charset()

        if not charset:
            charset = "iso-8859-1"

        body = unicode(email.get_payload(decode=True), charset)

    return body

def mime_message(msg_subject, msg_from, msg_to, \
                 plain_msg_body, html_msg_body=None, encoding="utf-8"):

    if not plain_msg_body:
        raise Exception("Plain text body is mandatory!")

    Charset.add_charset(encoding, Charset.QP, Charset.QP, encoding)

    if not html_msg_body:
        msg = MIMEText(plain_msg_body.encode(encoding), "plain", encoding.upper())
    else:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(plain_msg_body.encode(encoding), "plain", encoding.upper()))
        msg.attach(MIMEText(html_msg_body.encode(encoding), "html", encoding.upper()))

    if msg_subject:
        msg["subject"] = Header(msg_subject.encode(encoding), encoding.upper())

    if msg_from:
        msg["from"] = encode_address(msg_from, encoding)

    if msg_to:
        msg["to"] = encode_address(msg_to, encoding)

    return msg

def sendmail(msg, hostname="localhost", port=25, connections = {}):
    """
    NOTE: Todos los componentes del correo deben ser cadenas unicode o
          contener únicamente caracteres ASCII
    """

    conn_id = hostname + str(port)

    if conn_id not in connections:
        connections[conn_id] = smtplib.SMTP(hostname, port)

    s = connections[conn_id]
    s.sendmail(msg["from"], msg["to"], msg_as_string(msg))

def msg_as_string(msg):
    fp = StringIO()
    g = Generator(fp, mangle_from_=False, maxheaderlen=60)
    g.flatten(msg)

    return fp.getvalue()

def encode_address(address, encoding):
    parts = re.split("<|>", address.replace("\"", ""))
    name = parts[0]

    if len(parts) > 1:
        name = Header(name.encode(encoding.lower()), encoding.upper()).encode()
        name += " <" + parts[1] + ">"

    return name

def dovecot_deliver(email, deliver_path="/usr/libexec/dovecot/deliver"):
    """
    Utilizamos el programa de línea de comandos:
    /usr/libexec/dovecot/deliver para entregar correos
    electrónicos a los destinatarios ya que es mucho
    más rápido que utilizar la infraestructura completa
    del MTA. 

    NOTE: El MTA debe estar configurado para utilizar
          el delivery agent de dovecot (LDA), de lo 
          contrario utilizar la función devpower.mail.sendmail
    """

    mailbox = extract_address(email["to"]).split("@")[0]
    vmail_user = "vmail"

    deliver_cmd = ["sudo", "-u", vmail_user, deliver_path]
    deliver_args = ["-d", mailbox]
    cmd = deliver_cmd + deliver_args

    ps = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdoutdata, stderrdata = ps.communicate(msg_as_string(email))
    retVal = ps.poll()

    if retVal != 0:
        raise Exception("Ocurrió un error al intentar enviar el correo")
