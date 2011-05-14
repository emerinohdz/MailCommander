# coding: utf-8

import os
import re

from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage

from Cheetah.Template import Template
from devpower.mail import unicode_email_body, mime_message, \
                          sendmail

class Notification:
    """
    This is the base class for all the notifications that wish
    to be sent using the Notifier
    """

    def __init__(self, title=None, sender=None, recipients=[], body={}):
        self.title = title
        self.sender = title
        self.recipients = recipients
        self.body = body

class Notifier:
    """
    Base class for notifiers
    """

    def send(self, notification):
        raise NotImplementedError

class EmailNotifier(Notifier):
    """
    This notifier sends Notifications through email
    """

    def __init__(self, host="localhost", port=25):
        self.host = host
        self.port = port

    def send(self, notification):
        text_body = notification.body["text"]
        html_body = None

        if "html" in notification.body:
            html_body = notification.body["html"]

        for recipient in notification.recipients:
            msg = mime_message(notification.title, notification.sender, \
                               recipient, text_body, html_body)

            sendmail(msg, self.host, self.port)

