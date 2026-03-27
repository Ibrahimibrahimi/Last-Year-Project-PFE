"""
Lesson Recommendation System
Exports: recommend_lessons(user, langs, completed_ids, top_n=3)
Uses pretrained model from model.pkl if available, else falls back to heuristic.
"""
from .use import recommend_lessons

__all__ = ["recommend_lessons"]
