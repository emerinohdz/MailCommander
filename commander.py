#!/usr/bin/env python26
# coding: utf-8
#
# Copyright (C) 2011 by Edgar Merino (http://devio.us/~emerino)
#
# Licensed under the Artistic License 2.0 (The License).
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#    http://www.perlfoundation.org/artistic_license_2_0
#
# THE PACKAGE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS
# IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES. THE IMPLIED
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
# NON-INFRINGEMENT ARE DISCLAIMED TO THE EXTENT PERMITTED BY YOUR LOCAL
# LAW. UNLESS REQUIRED BY LAW, NO COPYRIGHT HOLDER OR CONTRIBUTOR WILL
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
# DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THE PACKAGE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import os
import re
import logging

from commands import Command
from auth import PUBLIC_KEY

class AuthException(Exception):
    def __init__(self, msg, command):
        Exception.__init__(self, msg)

        self.command = command

class Commander:
    """
    Execute the given command, checking if the user is authorized
    to run it first
    """

    def __init__(self, auth):
        self.__auth = auth

    def execute(self, command, authkey=PUBLIC_KEY, data=None):
        auth = self.__auth

        # Verifica si el usuario está autorizado para ejecutar el comando
        if auth.authorized(command, authkey):
            output = command.execute(data)
        else:
            raise AuthException("User not authorized to execute command", command)

        return output

