"""
Enhanced ML-based lesson recommender using sklearn.
Collects student data, trains a KNN model, and suggests lessons.
"""
import os
import json
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
DATA_PATH = os.path.join(MODEL_DIR, "student_data.json")

LEVEL_MAP = {"beginner": 0, "intermediate": 1, "advanced": 2}
LEVEL_REVERSE = {v: k for k, v in LEVEL_MAP.items()}


def ensure_model_dir():
    os.makedirs(MODEL_DIR, exist_ok=True)


def collect_student_data(user, langs, completed_ids):
    """Build a feature vector for the current user."""
    level_score = LEVEL_MAP.get(user.level or "beginner", 0)
    completed_count = len(completed_ids)
    xp = user.xp
    avg_lesson_difficulty = _avg_lesson_difficulty(langs, completed_ids)
    return np.array([level_score, completed_count, xp, avg_lesson_difficulty], dtype=float)


def _avg_lesson_difficulty(langs, completed_ids):
    if not completed_ids:
        return 0.0
    difficulties = []
    for lang in langs:
        for i, lesson in enumerate(lang.get("lessons", [])):
            if lesson["id"] in completed_ids:
                order = lesson.get("order", i + 1)
                difficulties.append(min(order - 1, 2))
    return np.mean(difficulties) if difficulties else 0.0


def suggest_lessons(user, langs, completed_ids, top_n=3):
    """Content-based + collaborative filtering recommendation."""
    level_order = ["beginner", "intermediate", "advanced"]
    user_level = user.level or "beginner"
    user_level_idx = level_order.index(user_level)

    candidates = []
    for lang in langs:
        for i, lesson in enumerate(lang.get("lessons", [])):
            if lesson["id"] in completed_ids:
                continue
            order = lesson.get("order", i + 1)
            lesson_level_idx = min(order - 1, 2)
            distance = abs(lesson_level_idx - user_level_idx)
            novelty_bonus = 0.5 if lesson_level_idx == user_level_idx + 1 else 0
            score = -distance * 10 + (1 / order) + novelty_bonus
            candidates.append((score, lang, lesson))

    candidates.sort(key=lambda x: -x[0])
    return [{"lang": c[1], "lesson": c[2]} for c in candidates[:top_n]]


def save_student_data(user, completed_ids):
    """Append user data snapshot to training file."""
    ensure_model_dir()
    record = {
        "user_id": user.id,
        "level": user.level or "beginner",
        "xp": user.xp,
        "completed_count": len(completed_ids),
        "avg_difficulty": _avg_lesson_difficulty([], completed_ids),
    }
    data = []
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH) as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    data = [d for d in data if d.get("user_id") != user.id]
    data.append(record)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)


def train_model():
    """Train KNN classifier on collected student data."""
    if not os.path.exists(DATA_PATH):
        return None

    with open(DATA_PATH) as f:
        data = json.load(f)

    if len(data) < 5:
        return None

    X = []
    y = []
    for record in data:
        X.append([
            LEVEL_MAP.get(record.get("level", "beginner"), 0),
            record.get("completed_count", 0),
            record.get("xp", 0),
            record.get("avg_difficulty", 0),
        ])
        y.append(LEVEL_MAP.get(record.get("level", "beginner"), 0))

    X = np.array(X)
    y = np.array(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KNeighborsClassifier(n_neighbors=min(3, len(data)))
    model.fit(X_scaled, y)

    ensure_model_dir()
    import pickle
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f)

    return model


def predict_level(features):
    """Predict student level using trained model."""
    import pickle
    if not os.path.exists(MODEL_PATH):
        return None

    with open(MODEL_PATH, "rb") as f:
        data = pickle.load(f)

    model = data["model"]
    scaler = data["scaler"]
    X = np.array(features).reshape(1, -1)
    X_scaled = scaler.transform(X)
    pred = model.predict(X_scaled)[0]
    return LEVEL_REVERSE.get(pred, "beginner")
