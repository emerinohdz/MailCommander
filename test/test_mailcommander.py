# coding: utf-8

from unittest import TestCase, main

from scanner import MailScanner
from auth import AuthManager
from util import find_commands, Parsers
from commander import Commander

class TestMailCommander(TestCase):
    
    def __init__(self, name):
        TestCase.__init__(self, name)
        
        self.commands = find_commands("test/cmds/")

        self.auth = AuthManager("test/etc/users.auth")
        self.commander = Commander(self.auth)
        
        self.scanner = MailScanner(Parsers(self.commands))
        self.email = open("test/data/cmd.email").read()

    def test_commander(self):
        cmd_id, data, authkey = self.scanner.scan(self.email)

        command = self.commands[cmd_id]
        self.commander.execute(command, data, authkey)

        print command.output["text"]

if __name__ == "__main__":
    main()
