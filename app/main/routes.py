from . import main_bp
from flask_login import login_required
from flask import render_template


@main_bp.route("/")
def index():
    return render_template("landing.html")

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
