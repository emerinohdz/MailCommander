# coding: utf-8

import os
import MySQLdb

from string import Template
from commands import Command
from devpower.mail import mime_message, dovecot_deliver as sendmail

class DB:

    def __init__(self):
        self.db = MySQLdb.connect(user="postfix",
                                  passwd="kkck2010",
                                  host="localhost",
                                  db="postfix")

        self.cursor = self.db.cursor()

    def check_mailbox(self, account):
        # Verifica si la cuenta ya existe
        mailbox_exists = self.cursor.execute("""
            SELECT active FROM mailbox
            WHERE username = %s
        """, account.email_address)

        active = self.cursor.fetchone()[0] if mailbox_exists else False

        return mailbox_exists, active

    def activate_mailbox(self, account):
        self.cursor.execute("""
            UPDATE mailbox
            SET active=1,password = %s
            WHERE username = %s
        """, (account.email_address, account.encrypted_password))

    def insert_mailbox(self, account):
        maildir = "%s/%s/" % (account.domain, account.username)

        # Agrega la cuenta a la base de datos
        self.cursor.execute("""
            INSERT INTO mailbox (username, password, name, company,
                                 maildir, local_part, domain, created, 
                                 modified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, now(), now())
        """, (account.email_address, account.encrypted_password, \
              account.name, account.company, maildir, account.username, \
              account.domain))

        # Agrega el alias de la cuenta a la base de datos 
        # (requerido por postfixadmin)
        self.cursor.execute("""
            INSERT INTO alias (address,goto,domain,created,modified,active) 
            VALUES (%s, %s, %s, now(), now(), 1)
        """, (account.email_address, account.email_address, account.domain))

    def close(self):
        self.cursor.close()
        self.db.commit()

class AccountsCommand(Command):
    def __init__(self):
        Command.__init__(self, os.path.dirname(__file__))
        
        self.db = DB()

    def run(self, data):
        accepted_accounts = []
        declined_accounts = []
        
        for account in data[0]["accounts"]:
            try:
                self.process(account)
                accepted_accounts.append(account)
            except Exception, err:
                declined_accounts.append(account)
                #import traceback
                #traceback.print_exc()

        self.db.close()

        output_data = {"accepted_accounts": accepted_accounts, 
                       "declined_accounts": declined_accounts}        
        output_data.update(data[0])

        return output_data

    def process(self, account):
        raise NotImplementedError

class AccountsCreatorCommand(AccountsCommand):
    
    def __init__(self):
        AccountsCommand.__init__(self)

        self.id = "altas"
        self.text_template = self.template_dir + "/creator.tmpl"
        self.html_template = self.template_dir + "/creator.html.tmpl"
        self.parser_account_fields = ["c", "n", "p", "l", "a", "s"]
        self.new_accounts = []

    def process(self, account):
        mailbox_exists, active = self.db.check_mailbox(account)

        if active:
            raise Exception("La cuenta ya existe")

        if mailbox_exists:
            self.db.activate_mailbox(account)
        else:
            self.db.insert_mailbox(account)
            self.new_accounts.append(account)

    def run(self, data):
        output = AccountsCommand.run(self, data)

        for account in self.new_accounts:
            sendmail(self.__create_mime_message(account))

        return output

    def __create_mime_message(self, account):
        msg_subject = "Bienvenido"
        msg_from = "Administrador de sistemas <sysadmin@etesa.com.mx>"
        msg_to = account.email_address
        plain_body = open(self.template_dir + "/welcome.html").read()
        html_body = open(self.template_dir + "/welcome.txt").read()

        return mime_message(msg_subject, msg_from, msg_to, \
                            plain_body, html_body)

class PasswordChangerCommand(AccountsCommand):
    
    def __init__(self):
        AccountsCommand.__init__(self)

        self.id = "password"
        self.text_template = self.template_dir + "/changer.tmpl"
        self.html_template = self.template_dir + "/changer.html.tmpl"
        self.parser_account_fields = ["a", "s"]

    def process(self, account):
        mailbox_exists, active = self.db.check_mailbox(account)

        if not mailbox_exists:
            raise Exception("La cuenta no existe")

        self.db.activate_mailbox(account)

