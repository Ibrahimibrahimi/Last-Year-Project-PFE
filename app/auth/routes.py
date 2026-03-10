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
        Email = request.form.get("email").strip()
        password = request.form.get("password")
        
        # check if correct
        user = User.query.filter_by(email=Email).first()
        if user is None : # NOT EXIST = NONE => REDIRECT
            return render_template("/auth/login.html",email="Email not found")
        # verify infos
        if  not check_password_hash(user.password,password):
            return render_template("/auth/login.html",password="Wrong password")
        login_user(user) # use the primary key
        return render_template("home.html",total_students=0)
    return render_template("/auth/login.html")


@auth_bp.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST" :
        # get data from form
        username = request.form.get("firstname") + " " + request.form.get("lastname") 
        password = request.form.get("password")
        email = request.form.get("email")
        birth = request.form.get("birth")
        
        # if there is no user with same email
        
        user = User.query.filter_by(email=email).first()
        
        if  user :
            # return the page register.html but with error that user already exists + show option of login
            return render_template("/auth/register.html",email="Email already exists")
        # create
        db.session.add(User(email=email,
                            password= generate_password_hash(password),
                            username=username,
                            birth=datetime.strptime(birth,"%Y-%m-%d").date()
                            ))
        # log that a new user created
        current_app.logger.info(f"User created successfully email={email}")
        db.session.commit()
        print("="*50,"USER CREATED") # better to use logs
        return render_template("/auth/login.html")
    return render_template("/auth/register.html")


@login_required
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
