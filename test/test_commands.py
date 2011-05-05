#!/usr/bin/env python
#coding: utf-8
# 
# Ejemplo de cómo utilizar la API Commands.
#
# La clase de entrada es Command, la cual contiene
# el método "execute(data)", que se encarga de 
# transformar los datos de entrada que recibe mediante
# una lista que a su vez contiene diccionarios 
# de datos [{}, {}, ...].
# 
# Cada ejecución del comando puede producir un diccionario
# de datos que se pasará al parámetro "searchList" de la
# clase Cheetah.Template al momento en que se llame
# al attributo "output" del comando. El comando también 
# puede no generar salida (devolver None).

import os
from commands import Command

class TestCommand(Command):
    def __init__(self):
        Command.__init__(self, os.path.dirname(__file__))        

        self.text_template = self.template_dir + "test.tmpl"

    def process(self, data):
        # Aquí inicializarías la conexión con la base de datos para levantar
        # el reporte con los datos proporcionados, para este ejemplo
        # simplemente devolvemos el diccionario que se encuentra en el índice
        # 0 de data al q le agregamos la llave "id_reporte" q contiene el id
        # del reporte que se generaría para utilizarlo en el template "test.tmpl".
        # Generalmente, la salida del comando es la que se enviará por correo
        # electrónico a la persona que haya ejecutado el comando, en su caso
        # al socio que requiera atención de soporte.

        data[0].update({"id_reporte": "445"})

        return data[0]
        

data = [{"correo": "ptovta_veracruz@etesa.com.mx", "desc": "no prende el monitor", "componentes": "TODOS"}]

command = TestCommand()
command.execute(data)

print command.output["text"].encode("iso-8859-1")

