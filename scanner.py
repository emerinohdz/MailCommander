# coding: utf-8

import re

from devpower.mail import UnicodeParser, unicode_email_body, extract_address
from auth import AuthKey

class ScannerException(Exception):
    def __init__(self, msg, cmd_id):
        Exception.__init__(self, msg)

        self.cmd_id = cmd_id

class MailScanner:
    """
    Extract command id and its associated data from an email source
    """

    def __init__(self, parsers=None):
        self.__parsers = parsers

    def scan(self, email_source, parser):
        if not email_source:
            raise ScannerException("Email source is missing")

        if not parser:
            raise ScannerException("Parser is missing")

        email = UnicodeParser().parsestr(email_source)
        
        cmd_id = self.__get_command_id(email)
        data = self.__get_data(cmd_id, email, parser)
        authkey = self.__get_authkey(email, data)

        return cmd_id, data, authkey

    def __get_command_id(self, email):
        cmd_id = None

        # Buscamos en el asunto del correo
        email_subject = email["subject"].lower().lstrip().rstrip()

        subject_regex = "^(\w+:\s*)*@cmd:\s?(\w+)$"
        match = re.search(subject_regex, email_subject)

        if match:
            cmd_id = match.group(2)

        # Intenta buscar el comando en la cabecera "To:" del correo electrónico
        else:
            cmd_address = extract_address(email["to"])
            cmd_id = cmd_address.split("@")[0]

        return cmd_id

    def __get_data(self, cmd_id, email, parser):
        if not parser:
            if self.__parsers:
                parser = self.__parsers[cmd_id]
            else:
                raise ScannerException("Don't know how to parse data")

        try:
            data = parser.parse(unicode_email_body(email))
        except ParserException, err:
            raise ScannerException(err, cmd_id)

        if len(data) == 0:
            raise ScannerException("No hay datos para el comando '%s'" \
                                      % self.command.id)

        return data

    def __get_authkey(self, email, data):
        user_address = extract_address(email["from"])
        user_hashkey = self.__extract_hashkey(data)

        authkey = AuthKey(user_address, user_hashkey)

        return authkey

    def __extract_hashkey(self, data):
        if "auth-key" in data:
            return data["auth-key"].strip()

        return None

