from flask import render_template
import hashlib


class Utils(object):
    # I don't really use this method
    def send_output(self, file, type, message):
        if type == "error":
            return render_template(file, error=message)
        elif type == "success":
            return render_template(file, message=message)

    # I do use these 2 methods though
    def encryptPassword(self, password, md5=True):
        if md5 is not False:
            password = hashlib.md5(password.encode('utf-8')).hexdigest()

        hash = password[16:32] + password[0:16]
        return hash

    def getLoginHash(self, password, staticKey):
        hash = self.encryptPassword(password, False)
        hash += staticKey
        hash += 'Y(02.>\'H}t":E1'
        hash = self.encryptPassword(hash)
        return hash
