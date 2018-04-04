import re


class Config(object):
    def __init__(self, app):
        self.app = app
        self.config = {}

        self.build_configuration()

    def build_configuration(self):
        self.config["flask"] = {
            "host": "localhost",  # Change this to your server's IPv4 address or domain name
            "port": 81,           # You can change this to whatever you want, 5000 for example
            "debug": True         # If this is False, you won't see changes until app restart
        }
        self.config["db"] = {
            "host": "localhost",      # Your MySQL host - it should be localhost
            "user": "root",           # Your MySQL user - usually root
            "pass": "",               # Your MySQL user password
            "name": "houdini_latest"  # Your database name
        }
        self.config["keys"] = {
            "app_secret": "change_this",  # Change this, generate a random key http://randomkeygen.com
            "static_key": "houdini",      # Edit this if it's different, houdini by default
        }
        self.config["recaptcha"] = {
            "recaptcha_enabled": True,  # Enabled True or Disabled False
            "recaptcha_site_key": "",   # Add your recaptcha's public key
            "recaptcha_secret_key": ""  # Add your recaptcha's secret key
        }
        self.config["register"] = {
            "allowed_chars": re.compile(r"^[^<>/{}[\]~`]*$")  # Change this to allow more characters
        }
        self.config["player_rank"] = {
            0: "Member",
            1: "Moderator",
            2: "Administrator"
        }

        return self.config

    def set_flask_config(self, config):
        self.app.config["RECAPTCHA_ENABLED"] = config["recaptcha"]["recaptcha_enabled"]
        self.app.config["RECAPTCHA_SITE_KEY"] = config["recaptcha"]["recaptcha_site_key"]
        self.app.config["RECAPTCHA_SECRET_KEY"] = config["recaptcha"]["recaptcha_secret_key"]
