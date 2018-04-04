import bcrypt
import hashlib
import os
import re
from flask import Flask, redirect, url_for, request, flash, send_file, abort, escape
from flask import session as Session
from flask import render_template
from flask_recaptcha import ReCaptcha
from flask_sqlalchemy_session import flask_scoped_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Data.User import User
from Data.Igloo import Igloo
from Data.Postcard import Postcard

from Register import Register
from Settings import Settings
from Utils import Utils
from Avatar import Avatar

from Config import Config

app = Flask(__name__)

# This is what you mainly want to edit
config = Config(app).build_configuration()
Config(app).set_flask_config(config)

engine = create_engine("mysql://%s:%s@%s/%s" % (config["db"]["user"], config["db"]["pass"],
                                                config["db"]["host"], config["db"]["name"]))
session_factory = sessionmaker(bind=engine)
session = flask_scoped_session(session_factory, app)

recaptcha = ReCaptcha(app)
recaptcha.init_app(app)

Settings = Settings(session)
Utils = Utils()
Avatar = Avatar()


@app.route("/", methods=["GET", "POST"])
def index():
    # Redirects if the user is logged in
    if Session.get("user"):
        return redirect(url_for("dashboard"))

    # on submit (HTTP POST request), retrieve the username and the password
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # This is the user's database model, so we can easily access his columns (e.g. user.Username)
        user = session.query(User).filter_by(Username=username).first()

        # If the user exists, we do our little password checking process and if it's all good, we let him in!
        if user is not None:
            uppercasedHash = hashlib.md5(password.encode('utf-8')).hexdigest().upper()
            flashClientHash = Utils.getLoginHash(uppercasedHash, config["keys"]["static_key"])
            databasePassword = user.Password

            # Don't let him in if the password is incorrect!
            if not bcrypt.checkpw(flashClientHash.encode('utf-8'), databasePassword.encode('utf-8')):
                flash("The password is incorrect!", "danger")
                return render_template("index.html")

            # We initiate the session and append our keys
            Session["user"] = {
                "id": user.ID,
                "username": user.Username,
                "email": user.Email,
                "rank": config["player_rank"][user.Moderator]
            }

            Session["logged_in"] = True

            # Take the user to the dashboard if no errors are encountered !
            flash("You have successfully logged in!", "success")
            return redirect(url_for("dashboard"))

        else:
            # Ugh, you have to make an account first pft
            flash("That player doesn't exist", "danger")
            return render_template("index.html")
    else:
        # by default we want to show the page and the login form
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = Register(request.form)

    # If an HTTP request is made through POST and if the checks are valid, do the following steps
    if request.method == "POST" and form.validate():
        # The register class takes care of the checks, username too short etc

        username = form.username.data
        email = form.email.data
        password = form.password.data

        password_hash = hashlib.md5(password.encode('utf-8')).hexdigest().upper()
        client_hash = Utils.getLoginHash(password_hash, config["keys"]["static_key"])
        bcrypt_password = bcrypt.hashpw(client_hash, bcrypt.gensalt(12))

        username_exists = session.query(
            session.query(User).filter_by(Username=username).exists()
        ).scalar()

        email_exists = session.query(
            session.query(User).filter_by(Email=email).exists()
        ).scalar()

        if username_exists:
            flash("This username is already in use.", "danger")
            return render_template("register.html", form=form)
        elif email_exists:
            flash("This email is already in use.", "danger")
            return render_template("register.html", form=form)
        elif not config["register"]["allowed_chars"].match(username):
            flash("This username is not valid.", "danger")
            return render_template("register.html", form=form)

        if config["recaptcha"]["recaptcha_enabled"]:
            if not recaptcha.verify():
                flash("Something went wrong with the recaptcha, try again!", "danger")
                return render_template("register.html", form=form)

        # We add the user
        user = User(Username=username, Nickname=username, Password=bcrypt_password, Email=email,
                    Active=1, Color=1)
        session.add(user)
        session.commit()

        # We send a postcard
        postcard = Postcard(RecipientID=user.ID, Details="", Type=125)
        session.add(postcard)

        # We add the default color in his inventory
        user.Inventory = 1

        # We add his igloo
        igloo = Igloo(PenguinID=user.ID)
        session.add(igloo)

        session.commit()

        # We initiate the session and append our keys
        Session["user"] = {
            "id": user.ID,
            "username": user.Username,
            "email": user.Email,
            "rank": config["player_rank"][user.Moderator]
        }

        Session["logged_in"] = True

        flash("You have successfully registered!", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html", form=form)


@app.route("/dashboard")
def dashboard():
    # We can't let the player access the dashboard if he is not logged in!
    if Session.get("logged_in") is None:
        flash("You have to login first if you want to access the dashboard!", "warning")
        return redirect(url_for("index"))

    # Again, this is the user's database model
    user = session.query(User).filter_by(Username=Session["user"]["username"]).first()

    """ If the player is logged in we show the dashboard and pass in the user variable
        so we can access it by doing {{user.ColumnName}} in dashboard.html"""
    return render_template("dashboard.html", user=user)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    # Once again, if the user is not logged in, we can't let him access this page
    if Session.get("logged_in") is None:
        flash("You have to login first if you want to access the settings!", "warning")
        return redirect(url_for("index"))

    # And again, this is the user's database model
    user = session.query(User).filter_by(Username=Session["user"]["username"]).first()

    # If an HTTP request is made through POST, we retrieve what's been posted
    if request.method == "POST":
        # If the user is trying to change his password, execute the following steps
        if request.form["action"] == "Change Password":
            current_password = request.form["current_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            # Change that password
            Settings.change_password(user, current_password, new_password, confirm_password,
                                     config["keys"]["static_key"])
            return render_template("settings.html", user=user)

        # But if the user is trying to change his email, execute the following steps instead
        elif request.form["action"] == "Change Email":
            new_email = request.form["new_email"]
            confirm_email = request.form["confirm_email"]

            # Change the email
            Settings.change_email(user, new_email, confirm_email)
            return render_template("settings.html", user=user)

    # If the user is logged in, we can let him access the settings page
    return render_template("settings.html", user=user)


@app.route("/support", methods=["GET", "POST"])
def support():
    # Coming soon !
    flash("The support system is coming soon!", "info")
    if Session.get("logged_in") is None:
        return redirect(url_for("index"))
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    """ We basically remove the keys from our session we created above in the index method
        to require the player to log out the player. We also tell the player that he can't
        logout if he's not logged in"""
    if Session.get("logged_in") is None:
        flash("You are not logged in therefore you can't log out!", "danger")
        return redirect(url_for("index"))

    Session.clear()
    flash("You have successfully logged out!", "success")

    # And we redirect the player to the login page
    return redirect(url_for("index"))


@app.route('/<path:m>/crossdomain.xml', methods=['GET'])
@app.route('/crossdomain.xml', methods=['GET'])
def handleCrossdomain(m=None):
    # We need some rights, right ?
    return '<cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>'


# Well I guess you don't really want to edit this method anyway
@app.route("/avatar/<id>/cp", methods=['GET'])
def getAvatar(id):
    # I edited some parts of this and made it more comprehensible because this dote ...

    # pretty self explanatory
    AVAILABLE_SIZES = [60, 88, 95, 120, 300, 600]

    # Again and again, this is the user's database model
    user = session.query(User).filter_by(ID=id).first()

    # By default the size is 120 if it's not specified in the URL (cp?size=integer)
    size = 120
    try:
        if "size" in request.args:
            size = int(request.args.get("size"))
            size = size if size in AVAILABLE_SIZES else 120
    except KeyError:
        pass

    details = [user.Photo, user.Color, user.Head, user.Face, user.Neck, user.Body, user.Hand,
               user.Feet, user.Flag]
    if details is None:
        return abort(404)

    items = Avatar.initializeImage(list(map(int, details)), size)

    return send_file(Avatar.buildAvatar(items), mimetype='image/png')


if __name__ == "__main__":
    app.secret_key = config['keys']['app_secret']
    app.run(host=config["flask"]["host"], port=config["flask"]["port"],
            debug=config["flask"]["debug"], threaded=True)  # Don't touch the threaded one
