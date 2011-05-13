# coding: utf-8

from hashlib import md5

class AuthKey:

    def __init__(self, user, hashkey, md5sum=True):
        self.user = user

        if hashkey and md5sum:
            self.hashkey = md5(hashkey).hexdigest()
        else:
            self.hashkey = hashkey

    def __eq__(self, other):
        if self.user != PUBLIC_ITEM and other.user != PUBLIC_ITEM and \
                self.user != other.user:

            return False

        if self.hashkey != PUBLIC_ITEM and other.user != PUBLIC_ITEM and \
                self.hashkey != other.hashkey:

            return False

        return True

    def items(self):
        return self.user, self.hashkey

class PublicItem():
    pass

PUBLIC_ITEM = PublicItem()
PUBLIC_KEY = AuthKey(None, None)

class AuthManager:

    def __init__(self, auth_file):
        self.keys = {}
        
        for line in open(auth_file, "r"):
            # Ignora comentarios
            if len(line.strip()) > 0 and line.lstrip()[:1] != "#":
                parts = line.split()
                
                if len(parts) != 3:
                    raise Exception("Datos inválidos en el archivo users.auth")

                parts = [p.strip() for p in parts]
                cmd, user, hashkey = parts

                if user == "*":
                    user = PUBLIC_ITEM

                if hashkey == "*":
                    hashkey = PUBLIC_ITEM

                if cmd not in self.keys:
                    self.keys[cmd] = []

                self.keys[cmd].append(AuthKey(user, hashkey, False))
        
    def authorized(self, cmd, auth_key):
        if cmd not in self.keys:
            raise Exception(\
                  "No se registró ningún usuario para el comando: %s" % (cmd))

        for key in self.keys[cmd]:
            if key == auth_key:
                return True

        return False

