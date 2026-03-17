from . import main_bp
from flask_login import login_required
from flask import render_template
import os
from app.models import User


@main_bp.route("/")
def index():

    N_LANGS = len(os.listdir("app/data"))
    N_LESSONS = len(os.listdir("app/data"))
    N_STUDENT = User.query.count()
    return render_template("landing.html",
                           n_langs=N_LANGS,
                           n_lessons=N_LESSONS,
                           n_students=N_STUDENT)


@main_bp.route("/courses")
@login_required
def courses():
    return render_template("courses.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/course/dd")
def course_detail():
    return render_template("course.html")
