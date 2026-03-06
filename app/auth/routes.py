from . import auth_bp
from app.extensions import login_manager
from flask import render_template , request, url_for , redirect
from flask_login import login_user , logout_user , login_required
from app.models import User
# organiser les paths de login et sign up only

@auth_bp.route("/login")
def login() :
    if request.method == "POST" :
        # get data from form
        email = request.form.get("email")
        password = request.form.get("password")
        
        
        # get the user id
        # !!! => save login using flask-login
        user = User.query.filter_by(email=email).first()
        login_user(user) # use the primary key
        return f"==> LOGIN {email} : {password}"
    return render_template("login.html")


@auth_bp.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST" :
        # get data from form
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        print(f"==> CREATED {username} : {password} :: {email}")
        return redirect("/login")
    return render_template("register.html")


@login_required
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@auth_bp.route("/a")
def f():
    return render_template("login.html")