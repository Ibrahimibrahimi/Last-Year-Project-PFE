from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.lessons import get_all_languages, get_language, save_language
from functools import wraps
import json, os, uuid

teacher_bp = Blueprint("teacher", __name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "teacher":
            flash("Teacher access required.", "danger")
            return redirect(url_for("main.landing"))
        return f(*args, **kwargs)
    return decorated


@teacher_bp.route("/dashboard")
@login_required
@teacher_required
def dashboard():
    langs = get_all_languages()
    total_lessons = sum(len(l.get("lessons", [])) for l in langs)
    return render_template("teacher/dashboard.html", langs=langs, total_lessons=total_lessons)


@teacher_bp.route("/language/new", methods=["GET", "POST"])
@login_required
@teacher_required
def new_language():
    if request.method == "POST":
        lang_id = request.form.get("lang_id", "").strip().lower().replace(" ", "_")
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        icon = request.form.get("icon", "").strip()
        if not lang_id or not name:
            flash("ID and name required.", "danger")
            return render_template("teacher/new_language.html")
        path = os.path.join(DATA_DIR, f"{lang_id}.json")
        if os.path.exists(path):
            flash("Language already exists.", "danger")
            return render_template("teacher/new_language.html")
        data = {"id": lang_id, "name": name, "icon": icon, "description": description, "lessons": []}
        save_language(lang_id, data)
        flash(f"Language '{name}' created!", "success")
        return redirect(url_for("teacher.dashboard"))
    return render_template("teacher/new_language.html")


@teacher_bp.route("/language/<lang_id>/lesson/new", methods=["GET", "POST"])
@login_required
@teacher_required
def new_lesson(lang_id):
    lang = get_language(lang_id)
    if not lang:
        flash("Language not found.", "danger")
        return redirect(url_for("teacher.dashboard"))

    if request.method == "POST":
        lesson_id = f"{lang_id[:2]}-les-{str(uuid.uuid4())[:6]}"
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        code_example = request.form.get("code_example", "").strip()
        xp = int(request.form.get("xp", 10))

        lesson = {
            "id": lesson_id,
            "order": len(lang["lessons"]) + 1,
            "title": title,
            "content": content,
            "code_example": code_example,
            "xp": xp,
            "lessons_required": [],
            "exercises": [],
        }
        lang["lessons"].append(lesson)
        save_language(lang_id, lang)
        flash(f"Lesson '{title}' created!", "success")
        return redirect(url_for("teacher.edit_lesson", lang_id=lang_id, lesson_id=lesson_id))

    return render_template("teacher/new_lesson.html", lang=lang)


@teacher_bp.route("/language/<lang_id>/lesson/<lesson_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def edit_lesson(lang_id, lesson_id):
    lang = get_language(lang_id)
    lesson = next((l for l in lang.get("lessons", []) if l["id"] == lesson_id), None)
    if not lesson:
        flash("Lesson not found.", "danger")
        return redirect(url_for("teacher.dashboard"))

    if request.method == "POST":
        lesson["title"] = request.form.get("title", "").strip()
        lesson["content"] = request.form.get("content", "").strip()
        lesson["code_example"] = request.form.get("code_example", "").strip()
        lesson["xp"] = int(request.form.get("xp", 10))
        save_language(lang_id, lang)
        flash("Lesson updated!", "success")
        return redirect(url_for("teacher.edit_lesson", lang_id=lang_id, lesson_id=lesson_id))

    return render_template("teacher/edit_lesson.html", lang=lang, lesson=lesson)


@teacher_bp.route("/language/<lang_id>/lesson/<lesson_id>/exercise/add", methods=["POST"])
@login_required
@teacher_required
def add_exercise(lang_id, lesson_id):
    lang = get_language(lang_id)
    lesson = next((l for l in lang.get("lessons", []) if l["id"] == lesson_id), None)
    if not lesson:
        flash("Lesson not found.", "danger")
        return redirect(url_for("teacher.dashboard"))

    ex_type = request.form.get("type", "mcq")
    question = request.form.get("question", "").strip()
    difficulty = request.form.get("difficulty", "easy")
    xp = int(request.form.get("xp", 5))
    hints = [h.strip() for h in request.form.get("hints", "").split("\n") if h.strip()]

    ex = {
        "id": f"{lesson_id}-ex-{str(uuid.uuid4())[:6]}",
        "order": len(lesson.get("exercises", [])) + 1,
        "type": ex_type,
        "difficulty": difficulty,
        "xp": xp,
        "question": question,
        "hints": hints,
    }

    if ex_type == "mcq":
        raw_options = request.form.get("options", "")
        options = [o.strip() for o in raw_options.split("\n") if o.strip()]
        ex["options"] = options
        ex["answer"] = request.form.get("answer", "").strip()
    else:
        ex["starter_code"] = request.form.get("starter_code", "").strip()
        ex["solution"] = request.form.get("solution", "").strip()

    lesson.setdefault("exercises", []).append(ex)
    save_language(lang_id, lang)
    flash("Exercise added!", "success")
    return redirect(url_for("teacher.edit_lesson", lang_id=lang_id, lesson_id=lesson_id))


@teacher_bp.route("/language/<lang_id>/lesson/<lesson_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete_lesson(lang_id, lesson_id):
    lang = get_language(lang_id)
    lang["lessons"] = [l for l in lang.get("lessons", []) if l["id"] != lesson_id]
    save_language(lang_id, lang)
    flash("Lesson deleted.", "info")
    return redirect(url_for("teacher.dashboard"))


@teacher_bp.route("/students")
@login_required
@teacher_required
def students():
    from app.models import User, LessonProgress
    all_students = User.query.filter_by(role="student").order_by(User.created_at.desc()).all()
    student_stats = []
    for s in all_students:
        completed = LessonProgress.query.filter_by(user_id=s.id, completed=True).count()
        started   = LessonProgress.query.filter_by(user_id=s.id).count()
        student_stats.append({
            "user": s,
            "completed": completed,
            "started": started,
        })
    return render_template("teacher/students.html", student_stats=student_stats)


@teacher_bp.route("/students/<int:student_id>")
@login_required
@teacher_required
def student_profile(student_id):
    from app.models import User, LessonProgress, ExerciseProgress, XPLog, Review
    from app.utils.lessons import get_all_languages
    from datetime import datetime, timedelta
    from app import db

    student = User.query.get_or_404(student_id)
    if student.role != "student":
        flash("User is not a student.", "danger")
        return redirect(url_for("teacher.students"))

    langs = get_all_languages()
    progress_records = LessonProgress.query.filter_by(user_id=student.id).all()
    completed_ids = {p.lesson_id for p in progress_records if p.completed}
    started_ids   = {p.lesson_id for p in progress_records}

    # XP chart — last 7 days
    xp_chart = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end   = day_start + timedelta(days=1)
        day_xp = db.session.query(db.func.sum(XPLog.amount)).filter(
            XPLog.user_id == student.id,
            XPLog.created_at >= day_start,
            XPLog.created_at < day_end,
        ).scalar() or 0
        xp_chart.append({"day": day.strftime("%a"), "xp": day_xp})

    recent_xp  = XPLog.query.filter_by(user_id=student.id).order_by(XPLog.created_at.desc()).limit(10).all()
    reviews    = Review.query.filter_by(user_id=student.id).order_by(Review.created_at.desc()).limit(10).all()
    stats      = student.get_stats_json()

    import json
    return render_template(
        "teacher/student_profile.html",
        student=student,
        langs=langs,
        completed_ids=completed_ids,
        started_ids=started_ids,
        xp_chart=json.dumps(xp_chart),
        recent_xp=recent_xp,
        reviews=reviews,
        stats=stats,
    )
