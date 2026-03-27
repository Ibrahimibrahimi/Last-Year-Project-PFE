"""
Lesson Recommender — Training Script
=====================================
Trains a KNN-based collaborative filtering model on student progress data
and saves the pretrained model to model.pkl.

Usage:
    python -m ML.recommender.train
    # or from project root:
    python ML/recommender/train.py
"""

import os
import json
import pickle
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
DATA_PATH  = os.path.join(os.path.dirname(__file__), "training_data.json")

LEVEL_MAP = {"beginner": 0, "intermediate": 1, "advanced": 2}


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_training_data():
    """
    Load student snapshots from training_data.json.
    Each record:
        {
          "user_id": int,
          "level": "beginner" | "intermediate" | "advanced",
          "xp": int,
          "completed_count": int,
          "completed_lesson_ids": ["py-les-01", ...]   # optional
        }
    Returns a list of dicts.
    """
    if not os.path.exists(DATA_PATH):
        print(f"[recommender] No training data found at {DATA_PATH}. Generating synthetic data.")
        return _generate_synthetic_data()

    with open(DATA_PATH) as f:
        data = json.load(f)

    if not data:
        print("[recommender] Training data is empty. Generating synthetic data.")
        return _generate_synthetic_data()

    return data


def _generate_synthetic_data(n=200):
    """Generate synthetic student records for bootstrapping the model."""
    rng = np.random.default_rng(42)
    records = []
    levels = ["beginner", "intermediate", "advanced"]
    for i in range(n):
        level = levels[rng.integers(0, 3)]
        level_idx = LEVEL_MAP[level]
        xp = int(rng.integers(0, 500) + level_idx * 300)
        completed = int(rng.integers(0, 10) + level_idx * 5)
        records.append({
            "user_id": i,
            "level": level,
            "xp": xp,
            "completed_count": completed,
        })
    return records


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def extract_features(records):
    """
    Convert a list of student records into a numpy feature matrix.
    Features: [level_idx, xp_normalized, completed_count_normalized]
    """
    if not records:
        return np.empty((0, 3))

    X = []
    xp_values = [r.get("xp", 0) for r in records]
    completed_values = [r.get("completed_count", 0) for r in records]

    xp_max = max(xp_values) if xp_values else 1
    completed_max = max(completed_values) if completed_values else 1

    for r in records:
        level_idx = LEVEL_MAP.get(r.get("level", "beginner"), 0)
        xp_norm = r.get("xp", 0) / (xp_max or 1)
        comp_norm = r.get("completed_count", 0) / (completed_max or 1)
        X.append([level_idx, xp_norm, comp_norm])

    return np.array(X, dtype=float)


# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------

class LessonRecommenderModel:
    """
    Lightweight KNN-based recommender.
    Given a student's feature vector it finds the K most similar students
    (from training data) and uses their level to calibrate recommendations.
    """

    def __init__(self, k=5):
        self.k = k
        self.X_train = None      # shape (n_students, 3)
        self.records  = None     # original records list

    def fit(self, records):
        """Fit the model on a list of student records."""
        self.records  = records
        self.X_train  = extract_features(records)
        print(f"[recommender] Trained on {len(records)} student records.")
        return self

    def _knn_profile(self, user_vec):
        """
        Returns the mean level_idx of the K nearest neighbours,
        which is used as a proxy difficulty target.
        """
        if self.X_train is None or len(self.X_train) == 0:
            return user_vec[0]  # fallback: use user's own level

        diffs = self.X_train - user_vec           # broadcast
        dists = np.linalg.norm(diffs, axis=1)
        nn_idx = np.argsort(dists)[: self.k]
        neighbour_levels = self.X_train[nn_idx, 0]  # level feature column
        return float(np.mean(neighbour_levels))

    def predict_difficulty_target(self, user_level, user_xp, completed_count):
        """
        Returns a float 0-2 representing the recommended difficulty target.
        """
        xp_max = float(max(self.X_train[:, 1].max() if self.X_train is not None and len(self.X_train) > 0 else 1, 1))
        comp_max = float(max(self.X_train[:, 2].max() if self.X_train is not None and len(self.X_train) > 0 else 1, 1))

        level_idx = LEVEL_MAP.get(user_level or "beginner", 0)
        xp_norm = user_xp / (xp_max * 500 or 1)   # crude normalisation
        comp_norm = completed_count / (comp_max * 10 or 1)

        user_vec = np.array([level_idx, min(xp_norm, 1.0), min(comp_norm, 1.0)])
        return self._knn_profile(user_vec)


# ---------------------------------------------------------------------------
# Train & save
# ---------------------------------------------------------------------------

def train_and_save():
    print("[recommender] Loading training data...")
    records = load_training_data()

    model = LessonRecommenderModel(k=5)
    model.fit(records)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"[recommender] Model saved to {MODEL_PATH}")
    return model


if __name__ == "__main__":
    train_and_save()
