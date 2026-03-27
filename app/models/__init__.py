from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="student")  # student | teacher
    level = db.Column(db.String(20), default=None)  # beginner | intermediate | advanced
    xp = db.Column(db.Integer, default=0)
    bio = db.Column(db.String(300), default="")
    avatar = db.Column(db.String(100), default="default.png")
    level_test_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    progress = db.relationship("LessonProgress", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", lazy=True)
    xp_logs = db.relationship("XPLog", backref="user", lazy=True)

    def total_lessons_completed(self):
        return LessonProgress.query.filter_by(user_id=self.id, completed=True).count()

    def total_lessons_started(self):
        return LessonProgress.query.filter_by(user_id=self.id).count()

    def get_stats_json(self):
        """Returns stats as a dict (stored concept in SQLite via JSON column)."""
        return {
            "username": self.username,
            "level": self.level,
            "xp": self.xp,
            "lessons_started": self.total_lessons_started(),
            "lessons_completed": self.total_lessons_completed(),
            "exercises_completed": ExerciseProgress.query.filter_by(user_id=self.id, completed=True).count(),
        }


class LessonProgress(db.Model):
    __tablename__ = "lesson_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lesson_id = db.Column(db.String(50), nullable=False)      # e.g. "py-les-01"
    language_id = db.Column(db.String(50), nullable=False)    # e.g. "python"
    completed = db.Column(db.Boolean, default=False)
    xp_earned = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # store stats snapshot as JSON string
    stats_snapshot = db.Column(db.Text, default="{}")

    def set_snapshot(self, data: dict):
        self.stats_snapshot = json.dumps(data)

    def get_snapshot(self):
        return json.loads(self.stats_snapshot)


class ExerciseProgress(db.Model):
    __tablename__ = "exercise_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_id = db.Column(db.String(50), nullable=False)
    lesson_id = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    xp_earned = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lesson_id = db.Column(db.String(50), nullable=False)
    language_id = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, default="")
    sentiment = db.Column(db.Integer, nullable=True)  # 1=positive, 0=negative, None=unclassified
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class XPLog(db.Model):
    __tablename__ = "xp_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MCQQuestion(db.Model):
    __tablename__ = "mcq_questions"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)   # JSON list
    answer = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # easy | medium | hard
    topic = db.Column(db.String(50), nullable=False)

    def get_options(self):
        return json.loads(self.options)
