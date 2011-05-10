# coding: utf-8

from commands import Command

class TestCommand(Command):
    def __init__(self):
        Command.__init__(self, "test")
