#!/usr/bin/env python26
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

__version__ = "0.5"
__author__ = "emerino <emerino at gmail dot com>"


import sys
import os
import re
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage

from Cheetah.Template import Template
from devpower.mail import UnicodeParser, unicode_email_body, \
                          mime_message, extract_address, \
                          dovecot_deliver as sendmail
from devpower.util import Properties

from commands import Command, find_commands
from auth import AuthManager

def main():
    cwd = os.getcwd() + "/"

    # Configuramos el log del sistema
    logging.basicConfig(filename=cwd+"var/log/commander.log", \
                        format="[%(asctime)s]: %(message)s", \
                        datefmt="%m/%d/%Y %I:%M:%S %p")

    # Inicialización del administrador de autorización/autenticación
    # y de la configuración del sistema
    auth = AuthManager(cwd + "etc/users.auth")
    conf = Properties(cwd + "etc/commander.conf")

    # Instancia de MailCommander
    commander = MailCommander(conf, auth)

    try:
        commander.run(sys.stdin.read(), sys.argv[1])
    except CommanderException, err:
        logging.error(str(err))

        send_error_email(conf["command_sender"], err.cmd_id, 
                         err.email, str(err), conf["lang"])

    except Exception, err:
        logging.error(str(err))

def send_error_email(msg_from, cmd_id, email, err, lang):
    msg_subject = "NO SE PUDO ENVIAR EL CORREO"
    msg_to = email["from"]

    searchList = {"command": cmd_id,
                  "error": unicode(err, "utf-8")}

    def msg_body(f):
        tmpl = Template(file=f, searchList=searchList)

        return unicode(tmpl)

    cwd = os.path.dirname(__file__) + "/lang/" + lang
    text_msg_body = msg_body(cwd + "/error.txt.tmpl")
    html_msg_body = msg_body(cwd + "/error.html.tmpl")

    msg = mime_message(msg_subject, msg_from, msg_to, \
                       text_msg_body, html_msg_body)

    msg_root = MIMEMultipart()
    msg_root["subject"] = msg_subject
    msg_root["from"] = msg_from
    msg_root["to"] = msg_to

    msg_root.attach(msg)
    msg_root.attach(MIMEMessage(email, "rfc822"))

    sendmail(msg_root)


class CommanderException(Exception):
    def __init__(self, msg, cmd_id, email):
        Exception.__init__(self, msg)

        self.cmd_id = cmd_id
        self.email = email

class MailCommander:

    def __init__(self, conf, auth):
        self.__auth = auth
        self.__conf = conf

    def run(self, email_source, user_ip):
        conf = self.__conf
        auth = self.__auth
        email = UnicodeParser().parsestr(email_source)

        command = self.__get_command(email)

        try:
            parser = command.parser
            data = parser.parse(unicode_email_body(email))
        except Exception, err:
            raise CommanderException(str(err), command.id, email)

        if len(data) == 0:
            raise CommanderException("No hay datos para el comando '%s'" \
                                     % command.id, command.id, email)

        user_address = extract_address(email["from"])
        user_hashkey = self.__extract_auth_key(data)

        # Verifica si el usuario está autorizado para ejecutar el comando
        if auth.authorized(command.id, user_address, user_ip, user_hashkey):
            try:
                command.execute(data)
            except Exception, err:
                raise CommanderException(str(err), command.id, email)

            recipients = [ key.email for key in \
                           auth.valid_keys(command.id) \
                           if key.email != "*"]

            msg_subject = data[0]["subject"]
            msg_from = conf["command_sender"]
            msg_to = data[0]["reply-to"]

            self.__send_cmd_notifications(msg_subject, msg_from, \
                                          msg_to, command.output["text"], \
                                          command.output["html"], recipients)

        # Envía notificaciones de autorización
        else:
            keys = [ key for key in auth.valid_keys(command.id) \
                     if key.email != "*"]

            self.__send_auth_notifications(email, conf["auth_sender"], keys)

    def __get_command(self, email):
        commands = find_commands(os.path.dirname(__file__), "cmds/")
        command_id = self.__find_command_id(email, commands)

        if command_id not in commands:
            raise CommanderException("Comando inválido: %s" % (command_id), \
                                     command_id, email)

        return commands[command_id]

    def __find_command_id(self, email, commands, where="to"):
        cmd_id = None

        # Intenta buscar el comando en la cabecera "To:" del correo electrónico
        if where == "to":
            cmd_address = extract_address(email["to"])
            cmd_id = cmd_address.split("@")[0]

            if cmd_id not in commands:
                cmd_id = self.__find_command_id(email, commands, "subject")

        # Buscamos en el asunto del correo
        elif where == "subject":
            email_subject = email["subject"].lower().lstrip().rstrip()

            subject_regex = "^(\w+:\s*)?(\w+).*$"
            match = re.search(subject_regex, email_subject)

            if match:
                cmd_id = match.group(2)

        return cmd_id

    def __extract_auth_key(self, data):
        auth_key = None

        if "auth-key" in data[0]:
            auth_key = data[0]["auth-key"].strip()

        return auth_key

    def __send_cmd_notifications(self, subject, msg_from, msg_to, text_body, \
                                 html_body, recipients):

        for recipient in recipients:
            msg = mime_message(subject, msg_from, recipient, \
                               text_body, html_body)
            sendmail(msg)
        
        msg = mime_message(subject, msg_from, msg_to, text_body, html_body)
        sendmail(msg)

    def __send_auth_notifications(self, subject, msg_from, email, keys):
        msg_body = self.__clean_body(unicode_email_body(email))
        msg_body = self.__insert_to_body(msg_body, "reply-to", email["from"])
        msg_body = self.__insert_to_body(msg_body, "subject", \
                                         "Re: " + email["subject"])

        for key in keys:
            body = msg_body

            if key.hashkey != "*":
                body = self.__insert_to_body(msg_body, "auth-key")

            msg = mime_message(subject, msg_from, key.email, body)
            sendmail(msg)

    def __clean_body(self, body):
        aux = re.split("<%|%>", body)[1]
        body = ""
        regex = "reply-to\s*:.*|subject\s*:.*|auth-key\s*:.*"

        for line in aux.split("\n"):
            if not re.search(regex, line, flags=re.IGNORECASE):
                # remove reply quotes
                body += re.sub("^\s*>+", "", line).lstrip()
                body += "\n"

        return "<%\n" + body + "%>"

    def __insert_to_body(self, body, key, value=""):
        prop = "%s: %s" % (key.upper(), value)
        
        return re.sub("<%.*\n", "<%\n" + prop + "\n", body)


if __name__ == "__main__":
    main()
