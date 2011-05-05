#!/usr/bin/env python
#coding: utf-8
#
# Ejemplo sobre cómo se utiliza un parser
#
# Esta parte no tienes que utilizarla directamente, 
# pero sirve para que veas que datos obtendrá el parser
# a partir del contenido del cuerpo del correo electrónico
# que se envíe.
#
#    El parser para los comandos reconoce una sintaxis muy sencilla
#    que debe ir delimitada mediante marcas específicas
#    ("<%" y "%>" de facto). Se reconocen dos tipos de elementos:
#
#    PROPIEDADES key:value
#    CUENTAS     con hasta 5 campos de información: 
#                empresa, nombre, puesto, sucursal, correo, password
#
#    El número y tipo de campos de las cuentas puede personalizarse, 
#    lo cual hace aún más flexible esta implementación.


from parser import Parser

email_body = """
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

parser = Parser()
data = parser.parse(email_body)

for key, value in data[0].items():
    print "%s: %s" % (key, value)

