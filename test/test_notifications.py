#coding: utf-8

from unittest import TestCase, main

from devpower.mail import UnicodeParser
from notifications import Notifier
from auth import AuthKey
from util import find_commands

class TestNotifications(TestCase):
    
    def __init__(self, name):
        TestCase.__init__(self, name)
        
        commands = find_commands("test/cmds/")
        self.command = commands["test"]

        conf = {
            "notification.sender": "sysadmin@etesa.com.mx",
            "commander.sender": "supercorreo@etesa.com.mx",
            "lang": "es"
        }

        keys = {"test": [AuthKey("emerino@etesa.com.mx", None)]}
        self.notifier = Notifier(conf, keys)

        self.email = UnicodeParser().parse(open("test/data/cmd.email"))

#    def test_auth_notification(self):
#        self.notifier.send_auth(self.command, self.email)

#    def test_auth_success(self):
#        data = {"subject": "MIRA ASUNTO", "key2": "something else"}
#        print data["subject"]

#        self.notifier.send_success(self.command, self.command.execute(data)["data"])

    def test_error(self):
        self.notifier.send_error("test", self.email, "UN ERROR!")

if __name__ == "__main__":
    main()
