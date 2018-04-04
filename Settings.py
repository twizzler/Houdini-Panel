from flask import flash
from validate_email import validate_email

from Data.User import User

import bcrypt
import hashlib

from Utils import Utils


class Settings(object):
    def __init__(self, session):
        self.session = session
        self.utils = Utils()

    def change_email(self, user, new_email, confirm_email):
        is_valid = validate_email(new_email)

        email_exists = self.session.query(
            self.session.query(User).filter_by(Email=new_email).exists()
        ).scalar()

        if not is_valid:
            return flash("The new email isn't valid!", "danger")
        elif new_email != confirm_email:
            return flash("The new emails don't match!", "danger")
        elif email_exists:
            return flash("The email already exists!")

        user.Email = new_email
        self.session.commit()

        return flash("You have successfully changed your email", "success")

    def change_password(self, user, current_password, new_password, confirm_password, staticKey):
        uppercasedHash = hashlib.md5(current_password.encode('utf-8')).hexdigest().upper()
        flashClientHash = self.utils.getLoginHash(uppercasedHash, staticKey)
        databasePassword = user.Password

        if not bcrypt.checkpw(flashClientHash.encode('utf-8'), databasePassword.encode('utf-8')):
            return flash("Current password is incorrect!", "danger")
        elif new_password != confirm_password:
            return flash("The new passwords don't match!", "danger")
        elif current_password == new_password:
            return flash("The new password can't be the current password!", "danger")
        elif len(new_password) < 4:
            return flash("The new password is too short", "danger")
        elif len(new_password) > 24:
            return flash("The new password is too long", "danger")

        newPasswordHash = hashlib.md5(new_password.encode('utf-8')).hexdigest().upper()
        flashClientHash = self.utils.getLoginHash(newPasswordHash, staticKey)

        bcryptPassword = bcrypt.hashpw(flashClientHash, bcrypt.gensalt(12))

        user.Password = bcryptPassword
        self.session.commit()

        return flash("You have successfully changed your password!", "success")