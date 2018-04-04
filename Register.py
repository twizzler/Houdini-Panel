from wtforms import Form, StringField, TextAreaField, PasswordField, validators


class Register(Form):
    username = StringField(u"Enter a username", [validators.length(min=4, max=50)])
    email = StringField(u"Enter your email", [validators.length(min=6, max=50)])
    password = PasswordField(u"Enter a password", [
        validators.DataRequired(),
        validators.EqualTo(u"confirm", message="Passwords do not match")
    ])
    confirm = PasswordField(u"Confirm your password")
