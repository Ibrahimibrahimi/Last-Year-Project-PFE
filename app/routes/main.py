from ML.chatbot import getDeepAiAnswer
from flask import Flask, request, jsonify
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, LessonProgress, ExerciseProgress, Review, XPLog
from app.utils.lessons import get_all_languages, get_language, get_lesson
import json
from datetime import datetime, timedelta
from flask import make_response
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    from app.utils.lessons import get_total_lessons
    langs = get_all_languages()
    total_users = User.query.count()
    total_lessons = get_total_lessons()
    total_completions = LessonProgress.query.filter_by(completed=True).count()
    return render_template(
        "landing.html",
        langs=langs,
        total_users=total_users,
        total_lessons=total_lessons,
        total_completions=total_completions,
    )


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "teacher":
        return redirect(url_for("teacher.dashboard"))

    langs = get_all_languages()
    progress_records = LessonProgress.query.filter_by(
        user_id=current_user.id).all()
    completed_ids = {p.lesson_id for p in progress_records if p.completed}
    started_ids = {p.lesson_id for p in progress_records}

    # XP over last 7 days for chart
    xp_chart = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        day_xp = db.session.query(db.func.sum(XPLog.amount)).filter(
            XPLog.user_id == current_user.id,
            XPLog.created_at >= day_start,
            XPLog.created_at < day_end,
        ).scalar() or 0
        xp_chart.append({"day": day.strftime("%a"), "xp": day_xp})

    # Filter suggested lessons by level
    suggested = []
    level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    user_level = current_user.level or "beginner"
    for lang in langs:
        for lesson in lang.get("lessons", []):
            if lesson["id"] not in completed_ids:
                suggested.append({"lang": lang, "lesson": lesson})
                if len(suggested) >= 6:
                    break
        if len(suggested) >= 6:
            break

    stats = current_user.get_stats_json()

    # ML suggestion (if model exists)
    ml_suggestions = []
    try:
        from ML.recommender import recommend_lessons
        ml_suggestions = recommend_lessons(current_user, langs, completed_ids)
    except Exception:
        try:
            from ml.recommender import suggest_lessons
            ml_suggestions = suggest_lessons(
                current_user, langs, completed_ids)
        except Exception:
            pass

    return render_template(
        "student/dashboard.html",
        langs=langs,
        suggested=suggested,
        ml_suggestions=ml_suggestions,
        completed_ids=completed_ids,
        started_ids=started_ids,
        stats=stats,
        xp_chart=json.dumps(xp_chart),
    )


@main_bp.route("/learn")
@login_required
def learn():
    langs = get_all_languages()
    progress = LessonProgress.query.filter_by(user_id=current_user.id).all()
    completed_ids = {p.lesson_id for p in progress if p.completed}
    started_ids = {p.lesson_id for p in progress}
    return render_template(
        "student/learn.html",
        langs=langs,
        completed_ids=completed_ids,
        started_ids=started_ids,
    )


@main_bp.route("/lesson/<lang_id>/<lesson_id>")
@login_required
def lesson(lang_id, lesson_id):
    lang = get_language(lang_id)
    lesson_data = get_lesson(lang_id, lesson_id)
    if not lang or not lesson_data:
        flash("Lesson not found.", "danger")
        return redirect(url_for("main.learn"))

    # Track start
    prog = LessonProgress.query.filter_by(
        user_id=current_user.id, lesson_id=lesson_id
    ).first()
    if not prog:
        prog = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            language_id=lang_id,
        )
        db.session.add(prog)
        db.session.commit()

    # Completed exercises
    completed_exercises = {
        ep.exercise_id
        for ep in ExerciseProgress.query.filter_by(
            user_id=current_user.id, lesson_id=lesson_id, completed=True
        ).all()
    }

    # Review for this lesson
    user_review = Review.query.filter_by(
        user_id=current_user.id, lesson_id=lesson_id
    ).first()
    all_reviews = Review.query.filter_by(lesson_id=lesson_id).order_by(
        Review.created_at.desc()).limit(10).all()

    avg_rating = 0
    if all_reviews:
        avg_rating = round(
            sum(r.rating for r in all_reviews) / len(all_reviews), 1)

    return render_template(
        "student/lesson.html",
        lang=lang,
        lesson=lesson_data,
        prog=prog,
        completed_exercises=completed_exercises,
        user_review=user_review,
        all_reviews=all_reviews,
        avg_rating=avg_rating,
    )


@main_bp.route("/lesson/<lang_id>/<lesson_id>/complete", methods=["POST"])
@login_required
def complete_lesson(lang_id, lesson_id):
    lesson_data = get_lesson(lang_id, lesson_id)
    if not lesson_data:
        return jsonify({"error": "Lesson not found"}), 404

    prog = LessonProgress.query.filter_by(
        user_id=current_user.id, lesson_id=lesson_id
    ).first()
    if not prog:
        prog = LessonProgress(user_id=current_user.id,
                              lesson_id=lesson_id, language_id=lang_id)
        db.session.add(prog)

    if not prog.completed:
        xp = lesson_data.get("xp", 10)
        prog.completed = True
        prog.xp_earned = xp
        prog.completed_at = datetime.utcnow()
        prog.set_snapshot(current_user.get_stats_json())
        current_user.xp += xp
        db.session.add(XPLog(user_id=current_user.id, amount=xp,
                       reason=f"Completed lesson: {lesson_data['title']}"))
        db.session.commit()
        # Save student data snapshot for recommender training
        try:
            import json as _json
            import os as _os
            data_path = _os.path.join(_os.path.dirname(_os.path.dirname(
                _os.path.dirname(__file__))), "ML", "recommender", "training_data.json")
            completed_ids_now = {
                p.lesson_id for p in current_user.progress if p.completed}
            record = {"user_id": current_user.id, "level": current_user.level,
                      "xp": current_user.xp, "completed_count": len(completed_ids_now)}
            existing = []
            if _os.path.exists(data_path):
                with open(data_path) as _f:
                    try:
                        existing = _json.load(_f)
                    except Exception:
                        existing = []
            existing = [r for r in existing if r.get(
                "user_id") != current_user.id]
            existing.append(record)
            with open(data_path, "w") as _f:
                _json.dump(existing, _f, indent=2)
        except Exception:
            pass
        return jsonify({"success": True, "xp": xp, "total_xp": current_user.xp})

    return jsonify({"already": True})


@main_bp.route("/exercise/<lang_id>/<lesson_id>/<exercise_id>/submit", methods=["POST"])
@login_required
def submit_exercise(lang_id, lesson_id, exercise_id):
    lesson_data = get_lesson(lang_id, lesson_id)
    if not lesson_data:
        return jsonify({"error": "Not found"}), 404

    exercise = next(
        (e for e in lesson_data.get("exercises", []) if e["id"] == exercise_id), None
    )
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    already = ExerciseProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id, completed=True
    ).first()
    if already:
        return jsonify({"already": True, "xp": 0})

    answer = request.json.get("answer", "").strip()
    correct = False
    if exercise["type"] == "mcq":
        correct = answer == exercise.get("answer", "")
    else:
        # code: simple solution match
        correct = answer.strip() == exercise.get("solution", "").strip()

    if correct:
        xp = exercise.get("xp", 5)
        ep = ExerciseProgress(
            user_id=current_user.id,
            exercise_id=exercise_id,
            lesson_id=lesson_id,
            completed=True,
            xp_earned=xp,
        )
        db.session.add(ep)
        current_user.xp += xp
        db.session.add(XPLog(user_id=current_user.id, amount=xp,
                       reason=f"Exercise {exercise_id}"))
        db.session.commit()
        return jsonify({"correct": True, "xp": xp, "total_xp": current_user.xp})

    return jsonify({"correct": False})


@main_bp.route("/lesson/<lang_id>/<lesson_id>/review", methods=["POST"])
@login_required
def add_review(lang_id, lesson_id):
    rating = int(request.form.get("rating", 0))
    comment = request.form.get("comment", "").strip()
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "danger")
        return redirect(url_for("main.lesson", lang_id=lang_id, lesson_id=lesson_id))

    # Classify sentiment
    sentiment = None
    if comment:
        try:
            from ML.review_classifier import classifier
            sentiment = classifier.classify(comment)
        except Exception:
            sentiment = None

    existing = Review.query.filter_by(
        user_id=current_user.id, lesson_id=lesson_id).first()
    if existing:
        existing.rating = rating
        existing.comment = comment
        if sentiment is not None:
            existing.sentiment = sentiment
    else:
        r = Review(
            user_id=current_user.id,
            lesson_id=lesson_id,
            language_id=lang_id,
            rating=rating,
            comment=comment,
        )
        if sentiment is not None:
            r.sentiment = sentiment
        db.session.add(r)
    db.session.commit()
    label = "😊 Positive" if sentiment == 1 else (
        "😞 Negative" if sentiment == 0 else "")
    flash(f"Review submitted! {label}", "success")
    return redirect(url_for("main.lesson", lang_id=lang_id, lesson_id=lesson_id))


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        bio = request.form.get("bio", "").strip()
        username = request.form.get("username", "").strip()
        if username and username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash("Username taken.", "danger")
                return redirect(url_for("main.profile"))
            current_user.username = username
        current_user.bio = bio
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("main.profile"))

    recent_xp = XPLog.query.filter_by(user_id=current_user.id).order_by(
        XPLog.created_at.desc()).limit(10).all()
    return render_template("student/profile.html", recent_xp=recent_xp)


@main_bp.route("/agent")
def agent():
    return render_template("agent.html")





@main_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    # Call your Python function
    answer = getDeepAiAnswer(user_message)
    return jsonify({'reply': answer})
