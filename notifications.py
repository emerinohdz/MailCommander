# coding: utf-8

import os
import re

from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage

from Cheetah.Template import Template
from devpower.mail import unicode_email_body, mime_message, \
                          sendmail

# TODO: Handle empty conf["commander.sender"] and conf["notification.sender"]
# TODO: Notifier should not depend con the Commands API at all
class Notifier:
    """
    This class is responsable for sending the required notifications
    to the required users.
    """
    
    def __init__(self, conf, keys):
        self.__conf = conf
        self.__keys = keys

    def send_success(self, command, data):
        conf = self.__conf
        keys = self.__keys

        recipients = [ key.user for key in keys[command.id] if key.user ]

        msg_subject = data["subject"]
        msg_from = conf["notification.sender"]

        if "reply-to" in data:
            recipients.append(data["reply-to"])

        text_body = command.output["text"]
        html_body = command.output["html"]

        for recipient in recipients:
            msg = mime_message(msg_subject, msg_from, recipient, \
                               text_body, html_body)
            sendmail(msg, "10.2.1.2", 25)
        

    def send_auth(self, command, email):
        conf = self.__conf
        keys = self.__keys

        keys = [ key for key in keys[command.id] if key.user ]

        msg_subject = "@CMD: %s" % (command.id)
        msg_from = conf["commander.sender"]

        msg_body = self.__clean_body(unicode_email_body(email))
        msg_body = self.__insert_to_body(msg_body, "reply-to", email["from"])
        msg_body = self.__insert_to_body(msg_body, "subject", \
                                         "Re: " + email["subject"])

        for key in keys:
            body = msg_body

            if key.hashkey: 
                body = self.__insert_to_body(msg_body, "auth-key")

            msg = mime_message(msg_subject, msg_from, key.user, body)
            sendmail(msg, "10.2.1.2", 25)

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

        msg_subject = "NO SE PUDO ENVIAR EL CORREO"
        msg_from = conf["notification.sender"]
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

        sendmail(msg_root, "10.2.1.2")

