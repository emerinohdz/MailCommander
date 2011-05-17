# coding: utf-8

import os
import re

from devpower.util import Properties
from Cheetah.Template import Template

from parser import DataParser, PropertiesParser

class PluginCommand:
    """
    This class wraps a command to easily find its parser and
    output templates, without modifying the Commands API
    """

    def __init__(self, command, cwd):
        self.__command = command
        self.__rel_plugin_dir = cwd
        self.__abs_plugin_dir = os.getcwd() + "/" + cwd
        
        self.__conf = None
        self.__parser = None
        self.__output_data = None
        self.__output = None

        # Initialize command
        self.__command.init()

    def execute(self, data):
        self.__output_data = self.__command.execute(data)

        return self.__output_data

    def __get_conf(self):
        if self.__conf:
            return self.__conf

        self.__conf = {}

        for root, dirs, files in os.walk(self.__abs_plugin_dir):
            for name in files:
                if name == "command.conf":
                    props = Properties(root + "/" + name)
                    
                    for k, v in props.items():
                        parts = k.split(".")
                        cmd = parts[0]
                        option = '.'.join(parts[1:])

                        if cmd == self.__command.id:
                            self.__conf[option] = v

        # initialize command with parameters from configuration
        self.__command.init(self.__conf)

        return self.__conf

    def __get_parser(self):
        if self.__parser:
            return self.__parser

        if "parser" in self.conf:
            parser = self.__inst_parser(self.conf["parser"])()
        else:
            parser = PropertiesParser()

        options_regex = re.compile("^parser\.options\.(\w+)$")

        for key, value in self.conf.items():
            match = options_regex.search(key)

            if match:
                if not parser.options:
                    parser.options = {}

                opt = match.group(1)
                parser.options[opt] = value

        self.__parser = parser

        return parser

    def __inst_parser(self, impl):
        # TODO: ????
        klass = {}
        klass["k"] = None

        def cls_found(k, cwd):
            if k.__name__ == impl:
                klass["k"] = k
                return False

            return True

        try:
            klass["k"] = eval(impl)
        except NameError, err:
            find_classes(DataParser, self.__rel_plugin_dir, cls_found)

        if not klass["k"]:
            raise Exception("Parser not found: %s" % (impl))

        return klass["k"]

    def __get_output(self):
        if self.__output:
            return self.__output

        if self.__output_data and len(self.__output_data) > 0:
            if "template.text" not in self.conf:
                raise Exception("Se necesita la plantilla de texto!")

            self.__output = {}

            text_file = self.__abs_plugin_dir + "/" + self.conf["template.text"]
            text = Template(file=text_file, searchList=[self.__output_data])

            self.__output["text"] = unicode(text)

            if "template.html" in self.conf:
                html_file = self.__abs_plugin_dir + "/" + \
                            self.conf["template.html"]

                html = Template(file=html_file, searchList=[self.__output_data])

                self.__output["html"] = unicode(html)
            else:
                self.__output["html"] = None

        return self.__output

    def __getattr__(self, attr):
        return getattr(self.__command, attr)

    conf = property(__get_conf)
    parser = property(__get_parser)
    output = property(__get_output)

