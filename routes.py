
from flask import render_template , url_for , redirect , request , session
from functions import session_exists , user_exists


def init_routes(app):
    @app.route("/")
    def home():
        # verify if there is a session , else => redirect to login
        Session = session.get("username")
        if Session :
            return render_template("home.html")
        else :
            return redirect(url_for("login"))
    @app.route("/login",methods=["POST","GET"])
    def login():
        if session_exists():
            if session.get("userid") :
                # seach if user exists
                user_still_exists = False # search in db
                if user_exists :
                    return redirect(url_for("home"))
                else :
                    session.clear()
            else :
                # erase session
                session.clear()
            return render_template("login.html")
        # if there is some post request 
        if request.method == "POST" :
            # get infos
            username = request.form.get("username")
            return user_exists(username)