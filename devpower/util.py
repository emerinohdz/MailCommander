# coding: utf-8
# 
# Implementación de un archivo .properties

import os

class Properties(dict):

    def __init__(self, file=None, separator=None):
        dict.__init__(self)

        self.separator = separator

        if file:
            self.__parse(file)

    def __parse(self, file):
        count = 0

        for line in open(file, "r"):
            count += 1

            # Ignora comentarios
            if len(line.strip()) > 0 and line.lstrip()[:1] != "#":
                parts = line.split("=")

                if len(parts) != 2:
                    raise Exception("Invalid syntax at line %d: %s" \
                                    % (count, line))

                key = parts[0].lstrip().rstrip()
                value = parts[1].lstrip().rstrip()

                self[key] = value

    def __setitem__(self, key, value):
        if self.separator:
            key = key.replace(" ", self.separator)

        dict.__setitem__(self, key, value)

# Código adaptado de http://www.luckydonkey.com/2008/01/02/python-style-plugins-made-easy/
# Originalmente creado por "dazza"
# 
# NOTE: Se agregó el parámetro relative_path, ya que el módulo base debe existir
# en sys.path, si sólo se pasa la ruta relativa y la aplicación no se
# ejecuta desde su directorio raíz el intérprete no podrá cargar el módulo
# ya que la ruta absoluta no se encuentra en sys.path.
#
# Además, para cada subclase que encuentra genera una instancia de la misma
def find_classes(cls, subdir="", root_path=None, listener_func=None):
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

    if not root_path:
        root_path = os.getcwd()

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
                        cwd = '/'.join(modulename.split(".")[:-1])
                        cont = listener_func(entry, cwd)

                    if not cont:
                        return
            except TypeError:
                #this happens when a non-type is passed in to issubclass. We
                #don't care as it can't be a subclass of Job if it isn't a
                #type
                continue

    for root, dirs, files in os.walk(root_path + "/" + subdir):
        root = root.split(root_path)[1][1:]

        for name in files:
            if name.endswith(".py") and not name.startswith("__"):
                path = os.path.join(root, name)
                modulename = path.rsplit('.', 1)[0].replace('/', '.')
                look_for_subclass(modulename)

