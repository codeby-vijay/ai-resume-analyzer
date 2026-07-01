"""Core ATS scoring pipeline.

Combines semantic similarity (sentence-transformers), skill extraction,
experience/education keyword matching, keyword density, and a formatting
heuristic into a single weighted 0-100 ATS score, along with matched/missing
skills and human-readable suggestions.

Model loading priority for the final ``ats_score``:
    1. Deep learning model  (ats_dl_model.pt)      → MODEL_SOURCE = "deep_learning"
    2. Classical ML model   (ats_score_model.joblib) → MODEL_SOURCE = "classical_ml"
    3. Heuristic weighted average (built-in)        → MODEL_SOURCE = "heuristic"

Component sub-scores (skill_match_score, experience_match_score, etc.)
are always computed by the heuristic functions regardless of which model
produces the final ats_score.
"""
import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from app.ml.preprocessing import clean_text
from app.ml.skills_data import (
    ALL_SKILLS, TECHNICAL_SKILLS, SOFT_SKILLS, CERTIFICATION_MAP,
    EDUCATION_KEYWORDS, EXPERIENCE_KEYWORDS,
)

logger = logging.getLogger(__name__)

# ---- Weighted scoring config -------------------------------------------------
WEIGHTS = {
    "skill_match": 0.40,
    "experience_match": 0.15,
    "education_match": 0.10,
    "keyword_density": 0.15,
    "formatting": 0.10,
    "semantic_similarity": 0.10,
}

_SAVED_MODELS_DIR = Path(__file__).resolve().parent / "saved_models"

# ---------------------------------------------------------------------------
# Sentence-transformers embedder (shared, cached)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Lazy model loaders (load once, cached at module level)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_dl_model():
    """Attempt to load the trained PyTorch DL model.

    Returns (model, meta_dict) or (None, None) on failure.
    """
    weights_path = _SAVED_MODELS_DIR / "ats_dl_model.pt"
    meta_path = _SAVED_MODELS_DIR / "ats_dl_model_meta.json"
    try:
        import torch
        from app.ml.dl_model import ATSScoreRegressor

        if not weights_path.exists():
            return None, None

        # Read meta to get embedding_dim
        meta = {}
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

        embedding_dim = meta.get("embedding_dim", 384)
        model = ATSScoreRegressor(embedding_dim=embedding_dim)
        state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
        model.load_state_dict(state_dict)
        model.eval()
        logger.info("Loaded DL model from %s", weights_path)
        return model, meta
    except Exception as exc:
        logger.warning("Could not load DL model: %s", exc)
        return None, None


@lru_cache(maxsize=1)
def _load_classical_model():
    """Attempt to load the trained scikit-learn model.

    Returns (model, meta_dict) or (None, None) on failure.
    """
    model_path = _SAVED_MODELS_DIR / "ats_score_model.joblib"
    meta_path = _SAVED_MODELS_DIR / "ats_score_model_meta.json"
    try:
        import joblib

        if not model_path.exists():
            return None, None

        model = joblib.load(model_path)
        meta = {}
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

        logger.info("Loaded classical ML model from %s", model_path)
        return model, meta
    except Exception as exc:
        logger.warning("Could not load classical ML model: %s", exc)
        return None, None


def get_active_model_info() -> dict:
    """Return information about which model is currently active.

    Used by the admin /model-info endpoint.
    """
    dl_model, dl_meta = _load_dl_model()
    if dl_model is not None:
        return {
            "model_source": "deep_learning",
            "metadata": dl_meta,
        }

    cl_model, cl_meta = _load_classical_model()
    if cl_model is not None:
        return {
            "model_source": "classical_ml",
            "metadata": cl_meta,
        }

    return {
        "model_source": "heuristic",
        "metadata": {
            "description": "Built-in weighted-average heuristic scorer",
            "weights": WEIGHTS,
        },
    }


# ---------------------------------------------------------------------------
# Component scoring functions
# ---------------------------------------------------------------------------

def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def semantic_similarity_score(resume_text: str, jd_text: str) -> float:
    """Returns 0-100 semantic similarity using sentence embeddings.
    Falls back to a bag-of-words Jaccard similarity if the embedding
    model is unavailable (e.g. offline environments)."""
    model = _get_embedder()
    if model is not None:
        embeddings = model.encode([resume_text, jd_text])
        sim = _cosine_similarity(embeddings[0], embeddings[1])
        return max(0.0, min(1.0, sim)) * 100
    # Fallback: Jaccard similarity on token sets
    a = set(clean_text(resume_text).split())
    b = set(clean_text(jd_text).split())
    if not a or not b:
        return 0.0
    jaccard = len(a & b) / len(a | b)
    return jaccard * 100


def extract_skills(text: str) -> List[str]:
    lowered = clean_text(text)
    found = []
    for skill in ALL_SKILLS:
        # match skill as whole word/phrase (handles multi-word skills too)
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, lowered):
            found.append(skill)
    return sorted(set(found))


def skill_match(resume_text: str, jd_text: str) -> Tuple[float, List[str], List[str]]:
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))

    if not jd_skills:
        # no identifiable required skills in JD -> neutral score
        return 70.0, sorted(resume_skills), []

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    score = (len(matched) / len(jd_skills)) * 100
    return score, matched, missing


def experience_match(resume_text: str, jd_text: str) -> float:
    lowered_resume = clean_text(resume_text)
    lowered_jd = clean_text(jd_text)

    # look for explicit years-of-experience requirement in JD, e.g. "3+ years"
    jd_years_match = re.search(r"(\d+)\+?\s*years?", lowered_jd)
    resume_years_matches = re.findall(r"(\d+)\+?\s*years?", lowered_resume)

    keyword_hits = sum(1 for kw in EXPERIENCE_KEYWORDS if kw in lowered_resume)
    keyword_score = min(keyword_hits / max(len(EXPERIENCE_KEYWORDS), 1), 1.0) * 60

    years_score = 0.0
    if jd_years_match:
        required_years = int(jd_years_match.group(1))
        resume_years = max((int(y) for y in resume_years_matches), default=0)
        if required_years == 0:
            years_score = 40.0
        else:
            years_score = min(resume_years / required_years, 1.0) * 40
    else:
        years_score = 40.0 if resume_years_matches else 20.0

    return round(keyword_score + years_score, 2)


def education_match(resume_text: str, jd_text: str) -> float:
    lowered_resume = clean_text(resume_text)
    lowered_jd = clean_text(jd_text)

    jd_requires_education = any(kw in lowered_jd for kw in EDUCATION_KEYWORDS)
    resume_has_education = [kw for kw in EDUCATION_KEYWORDS if kw in lowered_resume]

    if not jd_requires_education:
        return 80.0 if resume_has_education else 60.0

    if not resume_has_education:
        return 20.0

    # Reward matching degree level keywords, otherwise partial credit
    overlap = set(kw for kw in EDUCATION_KEYWORDS if kw in lowered_jd) & set(resume_has_education)
    if overlap:
        return 100.0
    return 55.0


def keyword_density_score(resume_text: str, jd_text: str) -> float:
    resume_tokens = clean_text(resume_text).split()
    jd_tokens = set(clean_text(jd_text).split())
    jd_tokens = {t for t in jd_tokens if len(t) > 3}  # ignore very short/common tokens

    if not jd_tokens or not resume_tokens:
        return 50.0

    resume_token_set = set(resume_tokens)
    overlap = jd_tokens & resume_token_set
    density = len(overlap) / len(jd_tokens)
    return round(min(density, 1.0) * 100, 2)


def formatting_score(resume_text: str) -> float:
    """Heuristic formatting/ATS-friendliness check: presence of standard
    section headers, reasonable length, no excessive special characters."""
    lowered = resume_text.lower()
    score = 100.0

    expected_sections = ["experience", "education", "skills"]
    missing_sections = [s for s in expected_sections if s not in lowered]
    score -= len(missing_sections) * 15

    word_count = len(resume_text.split())
    if word_count < 150:
        score -= 20  # too short, likely thin content
    elif word_count > 1200:
        score -= 10  # possibly too long for ATS parsing

    special_char_ratio = len(re.findall(r"[^\w\s]", resume_text)) / max(len(resume_text), 1)
    if special_char_ratio > 0.08:
        score -= 15  # heavy use of tables/graphics/symbols hurts ATS parsing

    return round(max(0.0, min(100.0, score)), 2)


def generate_strengths_weaknesses(scores: Dict[str, float]) -> Tuple[List[str], List[str]]:
    strengths, weaknesses = [], []
    labels = {
        "skill_match": "Skill alignment with the job description",
        "experience_match": "Relevant experience signals",
        "education_match": "Education requirements match",
        "keyword_density": "Keyword coverage from the job description",
        "formatting": "ATS-friendly formatting",
        "semantic_similarity": "Overall content relevance",
    }
    for key, label in labels.items():
        value = scores.get(key, 0)
        if value >= 75:
            strengths.append(f"{label} is strong ({value:.0f}/100).")
        elif value < 50:
            weaknesses.append(f"{label} needs improvement ({value:.0f}/100).")
    if not strengths:
        strengths.append("Resume was successfully parsed and analyzed.")
    if not weaknesses:
        weaknesses.append("No major weaknesses detected — great alignment overall.")
    return strengths, weaknesses


def generate_suggestions(missing_skills: List[str], scores: Dict[str, float]) -> List[str]:
    suggestions = []
    if missing_skills:
        top_missing = missing_skills[:6]
        suggestions.append(
            "Add or highlight these missing keywords/skills if you have relevant experience: "
            + ", ".join(top_missing) + "."
        )
    if scores.get("formatting", 100) < 70:
        suggestions.append(
            "Use clear standard section headers (Experience, Education, Skills) and avoid "
            "tables, graphics, or columns that ATS parsers may fail to read."
        )
    if scores.get("keyword_density", 100) < 60:
        suggestions.append(
            "Mirror more terminology from the job description throughout your bullet points, "
            "not just in a skills list."
        )
    if scores.get("experience_match", 100) < 60:
        suggestions.append(
            "Quantify your experience explicitly (e.g. '4 years of experience in...') to help "
            "both ATS systems and recruiters match seniority requirements."
        )
    if scores.get("education_match", 100) < 60:
        suggestions.append(
            "If applicable, ensure your degree/certification is clearly listed near the top of "
            "your Education section."
        )
    if not suggestions:
        suggestions.append("Your resume is well-aligned with this job description. Consider tailoring bullet points further for maximum impact.")
    return suggestions


def recommend_certifications(missing_skills: List[str]) -> List[str]:
    recs = []
    for skill in missing_skills:
        if skill in CERTIFICATION_MAP:
            recs.extend(CERTIFICATION_MAP[skill])
    # dedupe while preserving order
    seen = set()
    unique = []
    for r in recs:
        if r not in seen:
            unique.append(r)
            seen.add(r)
    return unique[:6]


# ---------------------------------------------------------------------------
# Model-based scoring helpers
# ---------------------------------------------------------------------------

def _predict_dl_score(resume_text: str, jd_text: str) -> float | None:
    """Run the DL model if available.  Returns score or None."""
    dl_model, _ = _load_dl_model()
    if dl_model is None:
        return None

    embedder = _get_embedder()
    if embedder is None:
        return None

    try:
        import torch

        embs = embedder.encode([resume_text, jd_text], convert_to_numpy=True)
        r_emb = embs[0]
        j_emb = embs[1]
        diff = r_emb - j_emb
        prod = r_emb * j_emb
        features = np.concatenate([r_emb, j_emb, diff, prod]).astype(np.float32)
        x = torch.tensor(features).unsqueeze(0)  # (1, input_dim)

        with torch.no_grad():
            pred = dl_model(x).item()
        return float(max(0.0, min(100.0, pred)))
    except Exception as exc:
        logger.warning("DL inference failed: %s", exc)
        return None


def _predict_classical_score(resume_text: str, jd_text: str) -> float | None:
    """Run the classical ML model if available.  Returns score or None."""
    cl_model, _ = _load_classical_model()
    if cl_model is None:
        return None

    try:
        from app.ml.features import extract_feature_vector

        vec = extract_feature_vector(resume_text, jd_text).reshape(1, -1)
        pred = cl_model.predict(vec)[0]
        return float(max(0.0, min(100.0, pred)))
    except Exception as exc:
        logger.warning("Classical ML inference failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_ats_analysis(resume_text: str, jd_text: str) -> dict:
    # ---- Component sub-scores (always computed) ----------------------------
    sem_score = semantic_similarity_score(resume_text, jd_text)
    sk_score, matched_skills, missing_skills = skill_match(resume_text, jd_text)
    exp_score = experience_match(resume_text, jd_text)
    edu_score = education_match(resume_text, jd_text)
    kw_score = keyword_density_score(resume_text, jd_text)
    fmt_score = formatting_score(resume_text)

    component_scores = {
        "skill_match": sk_score,
        "experience_match": exp_score,
        "education_match": edu_score,
        "keyword_density": kw_score,
        "formatting": fmt_score,
        "semantic_similarity": sem_score,
    }

    # ---- Determine ats_score via model cascade -----------------------------
    model_source = "heuristic"

    # Try DL model first
    dl_score = _predict_dl_score(resume_text, jd_text)
    if dl_score is not None:
        ats_score = round(dl_score, 2)
        model_source = "deep_learning"
    else:
        # Try classical ML model
        cl_score = _predict_classical_score(resume_text, jd_text)
        if cl_score is not None:
            ats_score = round(cl_score, 2)
            model_source = "classical_ml"
        else:
            # Fallback: heuristic weighted average
            ats_score = sum(component_scores[k] * WEIGHTS[k] for k in WEIGHTS)
            ats_score = round(max(0.0, min(100.0, ats_score)), 2)

    strengths, weaknesses = generate_strengths_weaknesses(component_scores)
    suggestions = generate_suggestions(missing_skills, component_scores)
    certifications = recommend_certifications(missing_skills)

    return {
        "ats_score": ats_score,
        "skill_match_score": round(sk_score, 2),
        "experience_match_score": round(exp_score, 2),
        "education_match_score": round(edu_score, 2),
        "keyword_density_score": round(kw_score, 2),
        "formatting_score": round(fmt_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "recommended_certifications": certifications,
        "MODEL_SOURCE": model_source,
    }
