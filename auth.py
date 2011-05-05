# coding: utf-8

from hashlib import md5

class AuthKey:

    def __init__(self, email, ip, hashkey):
        self.email = email
        self.ip = ip
        self.hashkey = hashkey

    def equals(self, email, ip, hashkey):
        if hashkey:
            hashkey = md5(hashkey).hexdigest()

        stored_key = self.items()
        given_key = (email, ip, hashkey)

        for i in range(3):
            stored = stored_key[i]
            given = given_key[i]

            if stored == "*" or stored == given:
                continue
            else:
                return False

        return True

    def items(self):
        return self.email, self.ip, self.hashkey

class AuthManager:

    def __init__(self, auth_file):
        self.keys = {}
        
        for line in open(auth_file, "r"):
            # Ignora comentarios
            if len(line.strip()) > 0 and line.lstrip()[:1] != "#":
                parts = line.split()
                
                if len(parts) != 4:
                    raise Exception("Datos inválidos en el archivo users.auth")

                cmd, email, ip, hashkey = parts

                if cmd not in self.keys:
                    self.keys[cmd] = []
                
                self.keys[cmd].append(AuthKey(email, ip, hashkey))
        
    def authorized(self, cmd, email, ip, hashkey):
        authorized = False

        if cmd not in self.keys:
            raise Exception(\
                  "No se registró ningún usuario para el comando: %s" % (cmd))

        for key in self.keys[cmd]:
            if key.equals(email, ip, hashkey):
                authorized = True
                break

        return authorized

    def valid_keys(self, cmd):
        if cmd not in self.keys:
            raise Exception(\
                  "No se registró ningún usuario para el comando: %s" % (cmd))

        return self.keys[cmd]

