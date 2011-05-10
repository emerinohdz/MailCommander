# coding: utf-8

import os

from commands import Command
from mailcommander import MailCommand

# Código adaptado de http://www.luckydonkey.com/2008/01/02/python-style-plugins-made-easy/
# Originalmente creado por "dazza"
# 
# NOTE: Se agregó el parámetro relative_path, ya que el módulo base debe existir
# en sys.path, si sólo se pasa la ruta relativa y la aplicación no se
# ejecuta desde su directorio raíz el intérprete no podrá cargar el módulo
# ya que la ruta absoluta no se encuentra en sys.path.
#
# Además, para cada subclase que encuentra genera una instancia de la misma
def find_classes(root_path, relative_path, cls, listener_func=None):
    """
    Find all subclass of cls in py files located below path
    (does look in sub directories)

    @param path: the path to the top level folder to walk
    @type path: str
    @param cls: the base class that all subclasses should inherit from
    @type cls: class
    @rtype: list
    @return: a list of instances that are subclasses of cls
    """

    def look_for_subclass(modulename):
        module=__import__(modulename)

        #walk the dictionaries to get to the last one
        d=module.__dict__
        for m in modulename.split('.')[1:]:
            d=d[m].__dict__

        #look through this dictionary for things
        #that are subclass of Job
        #but are not Job itself
        for key, entry in d.items():
            if key == cls.__name__:
                continue
            try:
                if issubclass(entry, cls):
                    if listener_func:
                        cwd = modulename.replace(".", "/")
                        cont = listener_func(entry, cwd)

                    if not cont:
                        return
            except TypeError:
                #this happens when a non-type is passed in to issubclass. We
                #don't care as it can't be a subclass of Job if it isn't a
                #type
                continue

    for root, dirs, files in os.walk(root_path + "/" + relative_path):
        for name in files:
            if name.endswith(".py") and not name.startswith("__"):
                root = root.split(root_path)[1][1:]
                path = os.path.join(root, name)
                modulename = path.rsplit('.', 1)[0].replace('/', '.')
                look_for_subclass(modulename)

def find_commands(root_path, relative_path):
    commands = {}
    configs = Configurations()

    for root, dirs, files in os.walk(root_path):
        for name in files:
            if name == "command.conf":
                configs.files.add(root + "/" + name)

    def command_found(klass, cwd):
        command = klass()

        if command.id:
            commands[command.id] = MailCommand(command, cwd)
        else:
            raise Exception("Command id is missing")

        return True

    find_classes(root_path, relative_path, Command, command_found)

    return commands

class Configurations(dict):
    def __init__(self):
        dict.__init__(self)

        self.files = set()
        self.__initialized = False

    def __getitem__(key):
        if not self.__initialized:
            for f in self.files:

            self.__initialized = True

        return dict.__getitem__(self, key)

# TODO: ????
def str_to_class(root_path, relative_path, cls, impl):
    klass = {}
    klass["k"] = None

    def cls_found(k, cwd):
        if k.__name__ == impl:
            klass["k"] = k
            return False

        return True

    try:
        klass["k"] = eval(impl)
    except NameError, err:
        find_classes(root_path, relative_path, cls, cls_found)

    if not klass["k"]:
        raise Exception("Class not found")

    return klass["k"]
