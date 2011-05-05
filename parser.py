# coding: utf-8

import crypt
import string
import subprocess
import re

from random import choice

class Account():

    COMPANIES = ("ABACO", "REFACIL", "ETESA", "CORPORATIVO", "DINAMO")

    def __init__(self, account_info):
        self.name = account_info[1]
        self.position = account_info[2]
        self.place = account_info[3]
        self.__set_email_address(account_info[4].lower())
        self.__set_password(account_info[5])
        self.__set_company(account_info[0])

    def __get_email_address(self):
        return "%s@%s" % (self.username, self.domain)

    def __set_email_address(self, address):
        self.username = None
        self.domain = None

        if address:
            if not re.search("^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$", address):
                raise Exception("Dirección de correo electrónico inválida: %s" % address)

            self.username, self.domain = address.split("@")

    def __get_company(self):
        return self.__company

    def __set_company(self, company):
        if company:
            company = company.upper()

        if company and company not in Account.COMPANIES:
            raise Exception("La empresa no es válida para la cuenta: %s" % (self.email_address))

        self.__company = company

    def __get_password(self):
        return self.__password

    def __set_password(self, password):
        if password == "-": # Generar
            letters = [choice(string.lowercase) for i in range(5)]
            digits = [choice(string.digits) for i in range(2)]

            password = ''.join(letters + digits)

        self.__password = password

    def __get_encrypted_password(self):
        # Salt de 8 dígitosutilizada en /etc/shadow y por postfixadmin
        salt = ''.join([choice(string.letters + string.digits) \
                        for i in range(8)])

        salt = "1$%s$" % (salt)

        return crypt.crypt(self.password, salt)

    def __str__(self):
        str = self.__attribute_as_string(self.company)
        str += self.__attribute_as_string(self.name)
        str += self.__attribute_as_string(self.position)
        str += self.__attribute_as_string(self.place)
        str += self.__attribute_as_string(self.email_address)
        str += self.__attribute_as_string(self.password)

        return str

    def __attribute_as_string(self, attribute):
        field = ""

        if attribute:
            field = attribute + "\n"

        return field
            
    company = property(__get_company, __set_company)
    email_address = property(__get_email_address, __set_email_address)
    password = property(__get_password, __set_password)
    encrypted_password = property(__get_encrypted_password)


class CommanderParser:
    """
    El parser para los comandos reconoce una sintaxis muy sencilla
    que debe ir delimitada mediante marcas específicas
    ("<%" y "%>" de facto). Se reconocen dos tipos de elementos:

    PROPIEDADES key:value
    CUENTAS     con hasta 5 campos de información: 
                empresa, nombre, puesto, sucursal, correo, password

    El número y tipo de campos de las cuentas puede personalizarse, 
    lo cual hace aún más flexible esta implementación.
    """

    def __init__(self, begin_delimiter="<%", end_delimiter="%>", \
            account_fields = None):

        if end_delimiter and not begin_delimiter:
            raise Exception("begin_delimiter missing")

        if begin_delimiter and not end_delimiter:
            raise Exception("end_delimiter missing")

        self.begin_delimiter = begin_delimiter
        self.end_delimiter = end_delimiter
        self.account_fields = account_fields

        # Tupla con los campos permitidos para cada cuenta
        # c = empresa
        # n = nombre
        # p = puesto
        # l = sucursal
        # a = dirección de correo electrónico (e.g. cuenta@etesa.com.mx)
        # s = contraseña de la cuenta
        self.__all_fields = ("c", "n", "p", "l", "a", "s")

    def get_lines(self, text):
        """
        Devuelve una lista con todas las líneas del texto dado, sin
        espacios en blanco.
        """

        self.__verify_delimiters(text)
        splitted_text = re.split("<%|%>", text)

        data = []

        # Si no hay delimitadores, ignora el contenido del correo
        if len(splitted_text) == 3:
            text = splitted_text[1]

            for line in text.split("\n"):
                line = self.__remove_reply_quotes(line)

                if len(line.strip()) != 0:
                    # Quita espacios antes/después de la información
                    data.append(line.lstrip().rstrip())

        return data

    def __verify_delimiters(self, lines):
        begin_count = lines.count("<%")
        end_count = lines.count("%>")

        if begin_count > 1 or end_count > 1:
            raise Exception("Wrong number of delimiters provided")

    def parse(self, text):
        """
        Devuelve una lista de grupos de información, en donde cada
        grupo contiene datos en un diccionario.
        """

        lines = self.get_lines(text)
        read_lines = 0
        data = []
        group_data = None

        # Parse groups of data
        while read_lines < len(lines):
            if not group_data:
                group_data = {}
                data.append(group_data)

            line = self.__remove_reply_quotes(lines[read_lines])
            property_regex = "^([a-zA-Z](\w|-|\s)*):(.+)$"

            match = re.search (property_regex, line)

            if match:
                group_data[match.group(1).strip().lower()] = \
                          match.group(3).lstrip().rstrip()

                read_lines += 1
            elif self.account_fields:
                accounts = self.__parse_accounts(lines[read_lines:])
                group_data["accounts"] = accounts

                read_lines += len(accounts) * len(self.account_fields)
                group_data = None

        return data

    def __remove_reply_quotes(self, line):
        match = re.search("^>+", line)

        if match:
            line = line[len(match.group(0)):].lstrip()

        return line
        
    def __parse_accounts(self, lines):
        accounts = []
        fields = self.account_fields
        read_lines = 0
        
        for line in lines:
            if not re.search("^[a-zA-Z](\w|-|\s)*:.+$", line): 
                read_lines += 1
            else:
                break

        lines = lines[:read_lines]

        if len(lines) % len(fields) != 0:
            raise Exception("Los datos proporcionados son incorrectos")

        for i in range(len(lines) / len(fields)):
            offset = len(fields) * i

            account = self.__get_account(lines[offset : len(fields) + offset], fields)
            accounts.append(account)

        return accounts

    def __get_account(self, account_info, fields):
        if "a" in fields:
            index = fields.index("a")
            account_info[index] = self.__fix_mail_address(account_info[index])

        if len(account_info) != 6:
            partial_info = account_info
            account_info = []

            for f in self.__all_fields:
                data = None

                if f in fields:
                    data = partial_info[fields.index(f)]

                account_info.append(data)

        return Account(account_info)

    def __fix_mail_address(self, address):
        """
        Cuando se envía un correo html y se toma la parte
        de texto del correo generalmente al tener una cadena
        que contenga una dirección de correo electrónico 
        aparece como "cuenta@dominio <mailto:..."
        Para evitar esto, la quinta línea que contiene la dirección
        de la cuenta de correo que se creará, se toma solo el primer
        elemento antes del primer espacio (string.split())
        """

        if re.search("<mailto:.*@.*>$", address):
            address = address.split()[0]

        return address


