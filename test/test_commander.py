# coding: utf-8

import unittest

from auth import AuthManager, AuthKey
from commander import Commander
from util import find_commands

class TestCommander(unittest.TestCase):
    
    def __init__(self, name):
        unittest.TestCase.__init__(self, name)

        commands = find_commands("test/cmds/")

        name = "test"
        self.command = commands[name]

        self.data = {
            "name": "MR SCRUFF",
            "hobby": "scruff",
            "color": "yellow"
        }

    def test_exec(self):
        auth = AuthManager("test/etc/users.auth")
        authkey = AuthKey(None, "7rus7.me")

        commander = Commander(auth)
        
        print commander.execute(self.command, self.data, authkey)

if __name__ == "__main__":
    unittest.main()
