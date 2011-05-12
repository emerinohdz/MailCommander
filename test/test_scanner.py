# coding: utf-8

import os

from scanner import MailScanner
from parser import PropertiesParser

scanner = MailScanner()

email_file = os.getcwd() + "/test/data/cmd.email"
email = open(email_file).read()

cmd_id, data, authkey = scanner.scan(email, PropertiesParser())


print cmd_id
print authkey.items()
print data
