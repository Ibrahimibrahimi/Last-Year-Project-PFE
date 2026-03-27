"""
Lesson Recommender — Inference
================================
Loads the pretrained model (model.pkl) and exposes recommend_lessons().
Falls back to a heuristic if the model file is missing.
"""

import os
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

LEVEL_MAP = {"beginner": 0, "intermediate": 1, "advanced": 2}

_model = None   # module-level cache


def _load_model():
    global _model
    if _model is not None:
        return _model
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                _model = pickle.load(f)
            return _model
        except Exception as e:
            print(f"[recommender] Could not load model.pkl: {e}")
    return None


def recommend_lessons(user, langs, completed_ids, top_n=3):
    """
    Recommend `top_n` lessons for `user` based on their progress.

    Parameters
    ----------
    user          : Flask-Login User object  (user.level, user.xp, user.id)
    langs         : list of language dicts   (from get_all_languages())
    completed_ids : set of lesson_id strings the user has already completed
    top_n         : number of recommendations to return

    Returns
    -------
    list of dicts: [{"lang": lang_dict, "lesson": lesson_dict}, ...]
    """
    model = _load_model()

    # --- collect candidate lessons ------------------------------------------
    level_order = ["beginner", "intermediate", "advanced"]
    user_level  = user.level or "beginner"
    user_level_idx = LEVEL_MAP.get(user_level, 0)

    # Get difficulty target from model (or fallback to user's own level)
    if model is not None:
        completed_count = len(completed_ids)
        difficulty_target = model.predict_difficulty_target(
            user_level, user.xp, completed_count
        )
    else:
        difficulty_target = float(user_level_idx)

    candidates = []
    for lang in langs:
        for i, lesson in enumerate(lang.get("lessons", [])):
            if lesson["id"] in completed_ids:
                continue
            order = lesson.get("order", i + 1)
            lesson_level_idx = min(order - 1, 2)   # map order → difficulty 0-2

            # Score: closer to difficulty_target = higher score
            distance = abs(lesson_level_idx - difficulty_target)
            score    = -distance * 10 + 1.0 / (order or 1)

            candidates.append((score, lang, lesson))

    candidates.sort(key=lambda x: -x[0])
    return [{"lang": c[1], "lesson": c[2]} for c in candidates[:top_n]]
