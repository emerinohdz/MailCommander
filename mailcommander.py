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

__version__ = "0.2"
__author__ = "emerino <emerino at gmail dot com>"


import sys
import os
import logging

from auth import AuthManager, AuthKey, PUBLIC_KEY
from scanner import MailScanner, ScannerException
from parser import ParserException
from notifications import Notifier
from util import Properties, Parsers, find_commands

def main():
    # Cofigure the system log
    configure_log()

    try:
        # Load system configuration
        conf = parse_arguments()

        # Send logging output to a file if specified
        if conf["log.file"]:
            configure_log(conf["log_file"])

        # Init the auth manager
        auth = AuthManager(conf["home.dir"] + "/users.auth")

        # Look for available commands
        commands = find_commands("cmds/")

        # Core components
        commander = Commander(auth)
        scanner = MailScanner(Parsers(commands))
        notifier = Notifier(conf, auth.keys)

        # Read the email from stdin
        email = sys.stdin.read()

        cmd_id, data, authkey = scanner.scan(email)
        output = commander.execute(commands[cmd_id], data, authkey)

        if output:
            notifier.send_success(command, data)
    except AuthException, err:
        # Send auth notifications
        notifier.send_auth(err.command, email)
    except ScannerException, err:
        logging.error(str(err))
        notifier.send_error(err.cmd_id, email, str(err))
    except Exception, err:
        logging.error(str(err))

def usage():
    print """
Usage: mailcommander.py <options>

Available options:
    -c, --config        path to configuration file 
                            default: /etc/MailCommander/commander.conf
    -h, --help          show this message

The email source should be passed through stdin.
    """

def parse_arguments():
    short_opts = "c:h"
    long_opts = ["config=", "help"]

    config = {}
    config_file = "/etc/MailCommander/commander.conf"

    if not os.path.exists(config_file):
        config_file = None

    default_config = { # defaults
        "home.dir": "/etc/MailCommander",
        "lang": "es",
        "commander.sender": None,
        "notification.sender": None,
        "log.file": None
    }

    opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)

    for opt, arg in opts:
        if opt == "--help":
            usage()
            sys.exit(0) # =(
        elif opt in ("--config", "-c"):
           config_file = arg 

    if config_file:
        config = Properties(config_file, separator=".")
        
    for opt, value in default_config.items():
        if opt not in config:
            config[opt] = value

    if not os.path.exists(config["home.dir"]):
        raise Exception("home dir '%s' does not exist!" % (conf["home.dir"]))
    elif config["home.dir"][-1] == "/":
        config["home.dir"] = config["home.dir"][:-1]

    return config

def configure_log(filename=None):
    if filename:
        logging.basicConfig(filename=conf["log.file"], \
                            format="[%(asctime)s]: %(message)s", \
                            datefmt="%m/%d/%Y %I:%M:%S %p")
    else:
        logging.basicConfig(format="[%(asctime)s]: %(message)s", \
                            datefmt="%m/%d/%Y %I:%M:%S %p")


if __name__ == "__main__":
    main()
