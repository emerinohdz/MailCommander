
import os

from parser import DataParser
from commands import Command
from util import find_classes, str_to_class, find_commands

def class_found(klass):
    print "Found: %s" % (klass.__name__)

cwd = os.getcwd() 

klass = str_to_class(cwd, "cmds", Command, "TestCommand")
print klass.__name__

#print find_commands(cwd, "cmds")
