# coding: utf-8

import os
import unittest

from util import find_commands
from plugin import PluginCommand

class TestPlugin(unittest.TestCase):
    
    def __init__(self, name):
        unittest.TestCase.__init__(self, name)

        commands = find_commands("test/cmds/")

        name = "test"
        self.command = commands[name]

        self.text = """
Texto que no sirve para aplicación puede ir en el correo
a manera de comentarios.

En este ejemplo se utiliza la llave "REPORTA" para saber
a nombre de quién se levantará el reporte, ya que podría
ser que el reporte se levante de una máquina con un correo
distinto.

Las llaves pueden ir en mayúsculas o minúsculas, el parser
las convertirá a minúsculas siempre.

La información a continuación es la de utilidad para los comandos:

<%

REPORTA: ptovta_veracruz@etesa.com.mx
DESC: El monitor no enciende
CoMPOnentES: Todos

%>
        """

    def get_data(self):
        parser = self.command.parser

        return parser.parse(self.text)

    def test_parser(self):
        data = self.get_data()

        print data

    def test_text_template(self):
        self.execute_command("text")

#    def test_html_template(self):
#        self.execute_command("html")

    def execute_command(self, output):
        data = self.get_data()
        self.command.execute(data)

        print self.command.output[output]

if __name__ == "__main__":
    unittest.main()
