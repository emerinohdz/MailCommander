# coding: utf-8

class Command:
    """
    A command is responsable for executing an arbitrary set of instructions.
    It does not impose any restrictions on what it may or may not
    execute, this is left to the sysadmin to decide.
    """
    
    def __init__(self, id):
        self.__id = id

    def execute(self, data):
        """
        Execute the command and return a data structure with the its output.
        """

        raise NotImplementedError

    def __get_id(self):
        return self.__id

    id = property(__get_id)

