from . import main_bp
from flask_login import login_required
from flask import render_template



@main_bp.route("/")
@login_required
def home():

    return "HOME"

@main_bp.route("/users")
def allUsers():
    # get all users
    from app.models import User
    Users = User.query.all()
    return render_template("users.html",users=Users,l=True if len(Users) != 0 else False)