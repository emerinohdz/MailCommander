# coding: utf-8
# 
# Implementación de un archivo .properties


class Properties(dict):

    def __init__(self, file=None, separator=None):
        dict.__init__(self)

        self.separator = separator

        if file:
            self.__parse(file)

    def __parse(self, file):
        count = 0

        for line in open(file, "r"):
            count += 1

            # Ignora comentarios
            if len(line.strip()) > 0 and line.lstrip()[:1] != "#":
                parts = line.split("=")

                if len(parts) != 2:
                    raise Exception("Invalid syntax at line %d: %s" \
                                    % (count, line))

                key = parts[0].lstrip().rstrip()
                value = parts[1].lstrip().rstrip()

                self[key] = value

    def __setitem__(self, key, value):
        if self.separator:
            key = key.replace(" ", self.separator)

        dict.__setitem__(self, key, value)

