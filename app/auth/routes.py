from . import auth_bp
from app.extensions import login_manager , db
from flask import current_app ,render_template , request, url_for , redirect
from flask_login import login_user , logout_user , login_required
from app.models import User
from  werkzeug.security import generate_password_hash , check_password_hash
from datetime import datetime
# organiser les paths de login et sign up only

@auth_bp.route("/login",methods=["POST","GET"])
def login() :
    if request.method == "POST" :
        # get data from form
        Email = request.form.get("email")
        password = request.form.get("password")
        
        # check if correct
        user = User.query.filter_by(email=Email).first()
        if not user : # NOT EXIST = NONE => REDIRECT
            logout_user()
            return render_template("login.html",email="Email not found")
        # verify infos
        if  check_password_hash(user.password,password):
            return render_template("login.html",password="Wrong password")
        login_user(user) # use the primary key
        return f"==> LOGIN {Email} : {password}"
    return render_template("login.html")


@auth_bp.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST" :
        # get data from form
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        birth = request.form.get("birth")
        bio = request.form.get("bio")
        
        # if there is no user with same email
        
        user = User.query.filter_by(email=email).first()
        
        if  user :
            # return the page register.html but with error that user already exists + show option of login
            return render_template("register.html",email_error="Email already exists")
        # create
        db.session.add(User(email=email,
                            password= generate_password_hash(password),
                            username=username,
                            birth=datetime.strptime(birth,"%Y-%m-%d").date(),
                            bio = bio
                            ))
        # log that a new user created
        current_app.logger.info(f"User created successfully email={email}")
        db.session.commit()
        print("="*50,"USER CREATED") # better to use logs
        return render_template("login.html",created="User created successfully , log in to show your profile")
    return render_template("register.html")


@login_required
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))
