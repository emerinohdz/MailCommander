
import os

from parser import DataParser
from commands import Command
from util import find_classes, find_commands

def class_found(klass, cwd):
    print "Found: %s" % (klass.__name__)

print "FIND CLASSES"
find_classes(Command, "cmds/", class_found)

print "FIND COMMANDS"
print find_commands("test/cmds/")

#print find_commands(cwd, "cmds")
