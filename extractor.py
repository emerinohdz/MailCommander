# coding: utf-8

from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage

from devpower.mail import UnicodeParser, unicode_email_body, \
                          mime_message, extract_address, \
                          dovecot_deliver as sendmail

from parser import DataParser, PropertiesParser

class ExtractorException(Exception):
    def __init__(self, msg, cmd_id):
        Exception.__init__(self, msg)

        self.cmd_id = cmd_id

class MailExtractor:
    """
    Extract command id and its associated data from an email source
    """

    def extract(self, email_source):
        email = UnicodeParser().parsestr(email_source)
        
        cmd_id = self.__get_command_id(email)
        data = self.__get_data(command, email)
        authkey = self.__authkey(email, data)

        return cmd_id, authkey, data

    def __get_command_id(self, email):
        cmd_id = None

        # Buscamos en el asunto del correo
        email_subject = email["subject"].lower().lstrip().rstrip()

        subject_regex = "^(\w+:\s*)?@CMD:\s?(\w+).*$"
        match = re.search(subject_regex, email_subject)

        if match:
            cmd_id = match.group(2)

        # Intenta buscar el comando en la cabecera "To:" del correo electrónico
        else:
            cmd_address = extract_address(email["to"])
            cmd_id = cmd_address.split("@")[0]

        return cmd_id

    def __get_data(self, command, email):
        parser = command.parser

        data = parser.parse(unicode_email_body(email))

        if len(data) == 0:
            raise ExtractorException("No hay datos para el comando '%s'" \
                                      % self.command.id, self.command.id)

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

