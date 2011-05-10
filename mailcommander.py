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

__version__ = "0.2"
__author__ = "emerino <emerino at gmail dot com>"


import sys
import os
import re
import logging

from Cheetah.Template import Template
from devpower.util import Properties

from commands import Command
from auth import AuthManager, AuthKey, PUBLIC_KEY
from util import find_commands, str_to_class

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
    
    commands = find_commands(cwd, "cmds")

    commander = Commander(auth)
    notifier = Notifier(auth, conf)
    extractor = MailExtractor()

    email = sys.stdin.read()

    try:
        cmd_id, authkey, data = extractor.extract(email)

        if cmd_id in commands:
            output = commander.execute(command, authkey, data)

            if output:
                notifier.send_success(command, data)
        else:
            logging.error(str(err))
            notifier.send_error(cmd_id, email, str(err))
    except AuthException, err:
        # Send auth notifications
        notifier.send_auth(err.command, email)
    except ExtractorException, err:
        logging.error(str(err))
        notifier.send_error(err.cmd_id, email, str(err))
    except Exception, err:
        logging.error(str(err))

class MailCommand:
"""
This class wraps a command to easily find its parser and
output templates, without modifying the Commands API
"""

    def __init__(self, command, cwd):
        self.__command = command
        self.__cwd = cwd

        self.__conf = None
        self.__parser = None
        self.__output_data = None
        self.__output = None

    def execute(self, data)
        self.__output_data = self.__command.execute(data)

        return self.__output_data

    def __get_conf(self):
        if self.__conf:
            return self.__conf

        self.__conf = {}

        for root, dirs, files in os.walk(cwd):
            for name in files:
                if name == "command.conf":
                    props = Properties(root + "/" + name)
                    
                    for k, v in props.items():
                        parts = k.split(".")
                        cmd = parts[0]
                        option = '.'.join(parts[1:])

                        if cmd == self.__command.id:
                            self.__conf[option] = v

        return self.__conf

    def __get_parser(self):
        if self.__parser:
            return self.__parser

        if "parser" in self.conf:
            parser = str_to_class(root, DataParser, self.conf["parser"])()
        else:
            parser = PropertiesParser()

        options_regex = re.compile("^parser\.options\.(\w+)$")

        for key, value in self.conf.items():
            match = options_regex.search(key)

            if match:
                if not parser.options:
                    parser.options = {}

                opt = match.group(1)
                parser.options[opt] = value

        self.__parser = parser

        return parser

    def __get_output(self):
        if self.__output_data and len(self.__output_data) > 0:
            if "text_template" not in self.conf:
                raise Exception("Se necesita la plantilla de texto!")

            self.__output = {}
            text = Template(file=self.__cwd + "/" + self.conf["text_template"],
                            searchList=[self.__output_data])

            self.__output["text"] = unicode(text)

            if "html_template" in self.conf:
                html_file = self.__cwd + "/" + self.conf["html_template"]
                html = Template(file=html_file,searchList=[self.__output_data])

                self.__output["html"] = unicode(html)
            else:
                self.__output["html"] = None

        return self.__output

    def __getattr__(self, attr):
        return getattr(self.__command, attr)

    conf = property(__get_conf)
    parser = property(__get_parser)
    output = property(__get_output)

class Notifier:
"""
This class is responsable for sending the required notifications
to the required users.
"""
    
    def __init__(self, conf, auth):
        self.__conf = conf
        self.__auth = auth

    def send_success(self, command, data):
        conf = self.__conf
        auth = self.__auth

        recipients = [ key.user for key in auth.keys[command.id] if key.user ]

        msg_subject = data["subject"]
        msg_from = conf["command_sender"]

        if "reply-to" in data:
            recipients.append(data["reply-to"])

        text_body = command.output["text"]
        html_body = command.output["html"]

        for recipient in recipients:
            msg = mime_message(msg_subject, msg_from, recipient, \
                               text_body, html_body)
            sendmail(msg)
        

    def send_auth(self, command, email)
        conf = self.__conf
        auth = self.__auth

        keys = [ key for key in auth.keys(command.id) if key.user ]

        msg_subject = "@CMD: %s" % (command.id)
        msg_from = conf["auth_sender"]

        msg_body = self.__clean_body(unicode_email_body(email))
        msg_body = self.__insert_to_body(msg_body, "reply-to", email["from"])
        msg_body = self.__insert_to_body(msg_body, "subject", \
                                         "Re: " + email["subject"])

        for key in keys:
            body = msg_body

            if key.hashkey: 
                body = self.__insert_to_body(msg_body, "auth-key")

            msg = mime_message(msg_subject, msg_from, key.user, body)
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

    def send_error(self, cmd_id, email, err):
        conf = self.__conf
        auth = self.__auth

        msg_subject = "NO SE PUDO ENVIAR EL CORREO"
        msg_from = conf["command_sender"]
        msg_to = email["from"]

        searchList = {"command": cmd_id,
                      "error": unicode(err, "utf-8")}

        def msg_body(f):
            tmpl = Template(file=f, searchList=searchList)

            return unicode(tmpl)

        cwd = os.getcwd() + "/lang/" + conf["lang"]
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


if __name__ == "__main__":
    main()
