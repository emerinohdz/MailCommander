# coding: utf-8

class Command:
    """
    A command is responsable for executing an arbitrary set of instructions.
    It does not impose any restrictions on what it may or may not
    execute, this is left to the sysadmin to decide.
    """
    
    def __init__(self, id):
        self.__id = id

    def init(self, config=None):
        """
        This method may be overriden in case additional configuration
        parameters wish to be passed externally to the command.
        """
        pass

    def execute(self, data):
        """
        Execute the command and return a data structure with its output.
        """

        raise NotImplementedError

    def __get_id(self):
        return self.__id

    id = property(__get_id)

