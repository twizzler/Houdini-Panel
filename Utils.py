from flask import render_template, flash, redirect, url_for
from functools import wraps
import hashlib


class Utils(object):
    # I don't really use this method
    def __init__(self, session=None):
        self.session = session

    def login_required(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if "logged_in" in self.session:
                return f(*args, **kwargs)
            else:
                flash("You need to login first before doing this!", "danger")
                return redirect(url_for("index"))

        return wrap
    
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
