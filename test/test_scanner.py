# coding: utf-8

import os

from unittest import TestCase, main

from scanner import MailScanner
from parser import PropertiesParser

class TestMailScanner(TestCase):

    def test_scanner(self):
        scanner = MailScanner()

        email_file = os.getcwd() + "/test/data/cmd.email"
        email = open(email_file).read()

        cmd_id, data, authkey = scanner.scan(email, PropertiesParser())

        print cmd_id
        print authkey.items()
        print data

if __name__ == "__main__":
    main()
