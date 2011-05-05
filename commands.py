# coding: utf-8

import os

from parser import CommanderParser
from Cheetah.Template import Template

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
    
    def __init__(self, template_dir):
        self.id = None
        self.template_dir = template_dir 

        self.text_template = template_dir + "/output.tmpl"
        self.html_template = None

        self.parser_account_fields = None
        self.__parser = None

        self.__output_data = None
        self.__output = None

    def execute(self, data):
        """ 
        Ejecuta las acciones del comando y devuelve una estructura de datos
        que se pasará al argumento "searchList" de la clase Cheetah.Template
        para generar la salida del comando al llamar al atributo self.output
        """

        self.__output_data = self.run(data)

        return self.__output_data

    def run(self, data):
        """
        Este método es el que en realidad se encarga de ejecutar
        las acciones del comando, y es el que debe implementarse
        por las clases que utilicen la API.

        ESTE MÉTODO NO DEBE LLAMARSE DIRECTAMENTE, UTILIZAR
        execute(data).
        """

        raise NotImplementedError

    def __get_output(self):
        if self.__output_data and len(self.__output_data) > 0:
            if not self.text_template:
                raise Exception("Se necesita la plantilla de texto!")

            self.__output = {}
            self.__output["text"] = unicode(Template(file=self.text_template, \
                                            searchList=[self.__output_data]))

            if self.html_template:
                self.__output["html"] = unicode(Template(\
                                                file=self.html_template, \
                                                searchList=[self.__output_data]))
            else:
                self.__output["html"] = None

        return self.__output

    def __get_parser(self):
        if not self.__parser:
            self.__parser = CommanderParser(\
                            account_fields=self.parser_account_fields)

        return self.__parser

    output = property(__get_output)
    parser = property(__get_parser)

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
