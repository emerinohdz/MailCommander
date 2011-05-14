# coding: utf-8

import re

class ParserException(Exception):
    pass

class DataParser:

    def __init__(self, begin_delimiter="<%", end_delimiter="%>"):
        if end_delimiter and not begin_delimiter:
            raise ParserException("begin_delimiter missing")

        if begin_delimiter and not end_delimiter:
            raise ParserException("end_delimiter missing")

        self.begin_delimiter = begin_delimiter
        self.end_delimiter = end_delimiter

    def get_lines(self, text):
        """
        Return a list with all the lines of the given text, without
        white spaces.
        """

        self.__verify_delimiters(text)
        splitted_text = re.split("%s|%s" % (self.begin_delimiter, \
                                 self.end_delimiter), text)

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
        begin_count = lines.count(self.begin_delimiter)
        end_count = lines.count(self.end_delimiter)

        if begin_count > 1 or end_count > 1:
            raise ParserException("Wrong number of delimiters provided")

    def __remove_reply_quotes(self, line):
        match = re.search("^>+", line)

        if match:
            line = line[len(match.group(0)):].lstrip()

        return line
        

    def parse(self, text):
        raise NotImplementedError

# TODO: Support repeated properties
class PropertiesParser(DataParser):
    """
    This parser recognized a simple key:value pair property sintax:
    key : value

    This properties have to be delimited between specific tags
    ("<%" and "%>" are the default). 
    """

    def __init__(self, begin_delimiter="<%", end_delimiter="%>"):
        DataParser.__init__(self, begin_delimiter, end_delimiter)

    def parse(self, text):
        """
        Return a dictionary with information obtained from the given text
        """

        # TODO: verify this is OK
        if not text:
            return {}

        lines = self.get_lines(text)

        read_lines = 0
        data = {}
        property_regex = re.compile("^([a-zA-Z](\w|-|\s)*):(.+)$")

        # Parse key : value pairs
        while read_lines < len(lines):
            line = lines[read_lines]
            match = property_regex.search(line)

            if match:
                data[match.group(1).strip().lower()] = \
                     match.group(3).lstrip().rstrip()

            else:
                raise ParserException("Invalid sintax at line %d: %s" \
                                       % (read_lines, line))

            read_lines += 1

        return data

