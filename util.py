# coding: utf-8

import os
import re

from devpower.util import find_classes

from commands import Command
from plugin import PluginCommand
from notifications import Notification

def find_commands(relative_path):
    commands = {}

    def command_found(klass, cwd):
        command = klass()

        if command.id:
            commands[command.id] = PluginCommand(command, cwd)
        else:
            raise Exception("Command id is missing")

        return True

    find_classes(Command, relative_path, command_found)

    return commands

class Parsers(dict):
    """
    This dictionary is responsable for handling parsers for each command,
    and it's needed by the MailExtractor class. It is handled in a
    class so that parsers can be loaded at runtime instead of loading
    them all at once.
    """

    def __init__(self, commands):
        dict.__init__(self)

        self.__commands = commands

    def __getitem__(self, attr):
        if attr not in self.__commands:
            raise Exception("Command has no parser registered: %s" % (attr))

        return self.__commands[attr].parser

class AuthNotification(Notification):

    def __init__(self, cmd_id, sender, recipients, email, data):
        Notification.__init__(self)

        self.title = "@CMD: %s" % (cmd_id)
        self.sender = sender
        self.recipients = recipients
        self.body["text"] = self.__get_body(email, data.raw)

    def __get_body(self, headers, body):
        # top to bottom
        body = "-->\n\n" + body
        body = self.__add_property(body, "auth-key")
        body = self.__add_property(body, "reply-to", headers["from"])
        body = self.__add_property(body, "subject", "Re: " + headers["subject"])
        body = "<--\n" + body

        return body

    def __add_property(self, body, key, value=""):
        prop = "%s: %s" % (key, value)

        return prop + "\n" + body

class SuccessNotification(Notification):
    
    def __init__(self, sender, recipients, command, sprops):
        Notification.__init__(self)

        if "subject" in sprops:
            self.title = sprops["subject"]
        else:
            self.title = "Re: " + command.id

        if "reply-to" in sprops:
            recipients.append(sprops["reply-to"])

        self.recipients = recipients
        self.sender = sender
        self.body = command.output

