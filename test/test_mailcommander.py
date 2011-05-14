# coding: utf-8

from unittest import TestCase, main

from devpower.mail import UnicodeParser

from scanner import MailScanner
from auth import AuthManager
from util import find_commands, Parsers, AuthNotification, SuccessNotification
from notifications import EmailNotifier
from commander import Commander

class TestMailCommander(TestCase):
    
    def __init__(self, name):
        TestCase.__init__(self, name)
        
        self.commands = find_commands("test/cmds/")

        self.auth = AuthManager("test/etc/users.auth")
        self.commander = Commander(self.auth)
        
        self.scanner = MailScanner(Parsers(self.commands))
        self.email = UnicodeParser().parse(open("test/data/cmd.email"))

        self.notifier = EmailNotifier("10.2.1.2", 25)

    def test_commander(self):
        cmd_id, data, sprops, authkey = self.scanner.scan(self.email)

        command = self.commands[cmd_id]
        self.commander.execute(command, data, authkey)

        print command.output["text"]

    def test_auth_notification(self):
        cmd_id, data, sprops, authkey = self.scanner.scan(self.email)
        command = self.commands[cmd_id]

        self.commander.execute(command, data, authkey)

        sender = "test@example.com"
        recipients = ["emerino@etesa.com.mx"]

        notification = AuthNotification(cmd_id, sender, recipients,
                                        self.email, data)

        self.notifier.send(notification)

    def test_success_notification(self):
        cmd_id, data, sprops, authkey = self.scanner.scan(self.email)
        command = self.commands[cmd_id]

        self.commander.execute(command, data, authkey)

        sender = "test@example.com"
        recipients = []

        notification = SuccessNotification(sender, recipients, command, sprops)
        self.notifier.send(notification)

if __name__ == "__main__":
    main()
