# coding: utf-8

import os

class Command:
    """
    Un comando se encarga de ejecutar una acción específica. Puede contener
    un parser propio en caso de que el provisto por defecto no sea suficiente.
    Para la salida de datos se tiene un diccionario en donde se pueden
    especificar distintos tipos de salida dependiendo el formato de la misma,
    por defecto 2 formatos son soportados: texto y html.

    Para mantener separada la parte de la presentación de la salida se utiliza
    la librería Cheetah para el uso de plantillas.
    """
    
    def __init__(self, id):
        self.__id = id

        self.__output_data = None
        self.__output = None

    def execute(self, data):
        """ 
        Ejecuta las acciones del comando y devuelve una estructura de datos
        con información de salida del comando.
        """

        raise NotImplementedError

    def __get_id(self):
        return self.__id

    id = property(__get_id)

# Código adaptado de http://www.luckydonkey.com/2008/01/02/python-style-plugins-made-easy/
# Originalmente creado por "dazza"
# 
# NOTE: Se agregó el parámetro relative_path, ya que el módulo base debe existir
# en sys.path, si sólo se pasa la ruta relativa y la aplicación no se
# ejecuta desde su directorio raíz el intérprete no podrá cargar el módulo
# ya que la ruta absoluta no se encuentra en sys.path.
#
# Además, para cada subclase que encuentra genera una instancia de la misma
def find_commands(root_path, relative_path, cls=Command):
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

    commands={}

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
                    command = entry()

                    if command.id:
                        commands[command.id] = command
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

    return commands
