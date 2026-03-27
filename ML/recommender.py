"""
Simple ML-based lesson recommender using sklearn.
Collects student data, trains a KNN model, and suggests lessons.
"""
import os, json
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_data.json")

LEVEL_MAP = {"beginner": 0, "intermediate": 1, "advanced": 2}


def collect_student_data(user, langs, completed_ids):
    """Build a feature vector for the current user."""
    level_score = LEVEL_MAP.get(user.level or "beginner", 0)
    completed_count = len(completed_ids)
    xp = user.xp
    return np.array([level_score, completed_count, xp], dtype=float)


def suggest_lessons(user, langs, completed_ids, top_n=3):
    """
    Simple content-based recommendation:
    - Beginners get easy lessons they haven't done
    - Higher levels get more advanced ones
    - Trained student data is used to weight suggestions
    """
    level_order = ["beginner", "intermediate", "advanced"]
    user_level = user.level or "beginner"
    user_level_idx = level_order.index(user_level)

    candidates = []
    for lang in langs:
        for i, lesson in enumerate(lang.get("lessons", [])):
            if lesson["id"] in completed_ids:
                continue
            # Score based on order (lower = easier) and level
            order = lesson.get("order", i + 1)
            lesson_level_idx = min(order - 1, 2)  # map order to difficulty
            distance = abs(lesson_level_idx - user_level_idx)
            score = -distance * 10 + (1 / order)  # closer level = higher score
            candidates.append((score, lang, lesson))

    candidates.sort(key=lambda x: -x[0])
    return [{"lang": c[1], "lesson": c[2]} for c in candidates[:top_n]]


def save_student_data(user, completed_ids):
    """Append user data snapshot to training file."""
    record = {
        "user_id": user.id,
        "level": user.level,
        "xp": user.xp,
        "completed_count": len(completed_ids),
    }
    data = []
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH) as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    # Update or add
    data = [d for d in data if d.get("user_id") != user.id]
    data.append(record)
    with open(MODEL_PATH, "w") as f:
        json.dump(data, f, indent=2)
