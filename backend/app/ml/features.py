"""Feature engineering for the classical ML ATS scoring model.

Builds a fixed-length numeric feature vector from a (resume_text, jd_text)
pair by reusing the existing component scoring functions from pipeline.py and
adding handcrafted structural features.

Feature vector layout (13 features):
    [0]  skill_match_score        – 0-100, from pipeline.skill_match()
    [1]  experience_match_score   – 0-100, from pipeline.experience_match()
    [2]  education_match_score    – 0-100, from pipeline.education_match()
    [3]  keyword_density_score    – 0-100, from pipeline.keyword_density_score()
    [4]  formatting_score         – 0-100, from pipeline.formatting_score()
    [5]  semantic_similarity      – 0-100, from pipeline.semantic_similarity_score()
    [6]  resume_word_count        – integer, total words in resume
    [7]  jd_word_count            – integer, total words in JD
    [8]  length_ratio             – float,  resume_words / jd_words (capped at 10)
    [9]  skill_overlap_ratio      – float,  |matched| / |jd_skills| (0 if no JD skills)
    [10] n_matched_skills         – integer, count of matched skills
    [11] n_missing_skills         – integer, count of missing skills
    [12] tech_soft_ratio          – float,  tech_skills / (tech_skills + soft_skills)
                                    in the resume (0.5 if no skills found)

Usage:
    from app.ml.features import extract_feature_vector, FEATURE_NAMES
    vec = extract_feature_vector(resume_text, jd_text)
    assert vec.shape == (len(FEATURE_NAMES),)
"""

from __future__ import annotations

import numpy as np

from app.ml.pipeline import (
    skill_match,
    experience_match,
    education_match,
    keyword_density_score,
    formatting_score,
    semantic_similarity_score,
    extract_skills,
)
from app.ml.skills_data import TECHNICAL_SKILLS

FEATURE_NAMES: list[str] = [
    "skill_match_score",
    "experience_match_score",
    "education_match_score",
    "keyword_density_score",
    "formatting_score",
    "semantic_similarity",
    "resume_word_count",
    "jd_word_count",
    "length_ratio",
    "skill_overlap_ratio",
    "n_matched_skills",
    "n_missing_skills",
    "tech_soft_ratio",
]

NUM_FEATURES = len(FEATURE_NAMES)


def extract_feature_vector(resume_text: str, jd_text: str) -> np.ndarray:
    """Return a 1-D float64 numpy array of shape (NUM_FEATURES,).

    Every element is a documented, deterministic numeric feature derived
    from the resume/JD pair.
    """
    # --- Component scores (reuse existing pipeline functions) ---------------
    sk_score, matched_skills, missing_skills = skill_match(resume_text, jd_text)
    exp_score = experience_match(resume_text, jd_text)
    edu_score = education_match(resume_text, jd_text)
    kw_score = keyword_density_score(resume_text, jd_text)
    fmt_score = formatting_score(resume_text)
    sem_score = semantic_similarity_score(resume_text, jd_text)

    # --- Structural features ------------------------------------------------
    resume_words = resume_text.split()
    jd_words = jd_text.split()
    resume_word_count = len(resume_words)
    jd_word_count = len(jd_words)
    length_ratio = (resume_word_count / jd_word_count) if jd_word_count > 0 else 0.0
    length_ratio = min(length_ratio, 10.0)  # cap to avoid outliers

    # Skill overlap ratio
    jd_skills = set(extract_skills(jd_text))
    n_matched = len(matched_skills)
    n_missing = len(missing_skills)
    skill_overlap_ratio = (n_matched / len(jd_skills)) if jd_skills else 0.0

    # Technical vs soft skill ratio in the resume
    resume_skills = set(extract_skills(resume_text))
    tech_set = set(TECHNICAL_SKILLS)
    n_tech = len(resume_skills & tech_set)
    n_soft = len(resume_skills - tech_set)
    tech_soft_ratio = (n_tech / (n_tech + n_soft)) if (n_tech + n_soft) > 0 else 0.5

    return np.array([
        sk_score,
        exp_score,
        edu_score,
        kw_score,
        fmt_score,
        sem_score,
        resume_word_count,
        jd_word_count,
        length_ratio,
        skill_overlap_ratio,
        n_matched,
        n_missing,
        tech_soft_ratio,
    ], dtype=np.float64)
