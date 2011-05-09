# coding: utf-8

from hashlib import md5

class AuthKey:

    def __init__(self, user, hashkey):
        self.user = user

        if hashkey:
            self.hashkey = md5(hashkey).hexdigest()
        else:
            self.hashkey = hashkey

    def __eq__(self, other):
        return self.user == other.user and self.hashkey == other.hashkey

    def items(self):
        return self.user, self.hashkey

PUBLIC_KEY = AuthKey(None, None)

class AuthManager:

    def __init__(self, auth_file):
        self.keys = {}
        self.admins = set()
        
        for line in open(auth_file, "r"):
            # Ignora comentarios
            if len(line.strip()) > 0 and line.lstrip()[:1] != "#":
                parts = line.split()
                
                if len(parts) != 3:
                    raise Exception("Datos inválidos en el archivo users.auth")

                parts = [p.strip() for p in parts]
                cmd, user, hashkey = parts

                if user == "*":
                    user = None

                if hashkey == "*":
                    hashkey = None

                if cmd not in self.keys:
                    self.keys[cmd] = []

                self.keys[cmd].append(AuthKey(user, hashkey))
        
    def authorized(self, cmd, auth_key):
        if cmd.id not in self.keys:
            raise Exception(\
                  "No se registró ningún usuario para el comando: %s" % (cmd))

        if self.__cmd_is_public(cmd.id):
            return True
        else:
            for key in self.keys[cmd.id]:
                if key == auth_key:
                    return True

    def __cmd_is_public(self, cmd):
        return self.keys[cmd][0] == PUBLIC_KEY

