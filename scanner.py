# coding: utf-8

import re

from devpower.mail import unicode_email_body, extract_address
from parser import PropertiesParser, ParserException
from auth import AuthKey

class ScannerException(Exception):
    def __init__(self, msg, cmd_id):
        Exception.__init__(self, msg)

        self.cmd_id = cmd_id

class Data(dict):
    def __init__(self, data):
        dict.__init__(self, data)

        self.raw = None

class MailScanner:
    """
    Extract command id, authkey and its associated data from an email 
    """

    def __init__(self, parsers=None):
        self.__parsers = parsers
        self.__sprops_parser = PropertiesParser("<--", "-->")

    def scan(self, email, parser=None):
        """
        Return a tuple containing the following:
        (cmd_id, data, sprops, authkey)

        where:
            cmd_id = Command ID
            data = Data for the command associated with cmd_id
            sprops = System properties
            authkey = The AuthKey for the command
        """

        if not email:
            raise Exception("Email is missing")

        cmd_id = self.__get_command_id(email)

        if not parser:
            if self.__parsers != None:
                parser = self.__parsers[cmd_id]
            else:
                raise ScannerException("Don't know how to parse data", cmd_id)

        email_body = unicode_email_body(email)
        data = self.__get_data(cmd_id, email_body, parser)
        data.raw = self.__clean_email_body(email_body, parser.begin_delimiter,\
                                           parser.end_delimiter, cmd_id)

        sprops = self.__get_sprops(email_body, cmd_id)
        authkey = self.__get_authkey(email, sprops)

        return cmd_id, data, sprops, authkey

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

    def __get_data(self, cmd_id, email_body, parser):
        try:
            data = Data(parser.parse(email_body))
        except ParserException, err:
            raise ScannerException(err, cmd_id)

        if not data:
            raise ScannerException("No data for command '%s'" \
                                    % (cmd_id), cmd_id)

        return data

    def __get_authkey(self, email, data):
        user_address = extract_address(email["from"])
        user_hashkey = self.__extract_hashkey(data)

        authkey = AuthKey(user_address, user_hashkey)

        return authkey

    def __extract_hashkey(self, data):
        if "auth-key" in data:
            authkey = data["auth-key"].strip()
            del(data["auth-key"])

            return authkey

        return None

    def __clean_email_body(self, body, start_delim, end_delim, cmd_id):
        aux = re.split("%s|%s" % (start_delim, end_delim), body)[1]
        body = ""

        for line in aux.split("\n"):
            # remove reply quotes
            line = re.sub("^\s*>+", "", line).lstrip()

            if line.strip():
                body += line + "\n"

        return start_delim + "\n" + body + "\n" + end_delim

    def __get_sprops(self, email_body, cmd_id):
        try:
            data = self.__sprops_parser.parse(email_body)
        except ParserException, err:
            raise ScannerException(err, cmd_id)

        return data

