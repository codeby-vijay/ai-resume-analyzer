"""Tests for the ML pipeline, feature engineering, and model loading.

These tests MUST pass without requiring model training — the heuristic
fallback path is the baseline that CI depends on.
"""

import os
import sys

import numpy as np
import pytest

# Ensure the backend package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.features import FEATURE_NAMES, NUM_FEATURES, extract_feature_vector
from app.ml.pipeline import run_ats_analysis

# ---------------------------------------------------------------------------
# Sample data used across tests
# ---------------------------------------------------------------------------

SAMPLE_RESUME = """
Alex Johnson
email: alex@email.com | phone: +1-555-0123

Skills
----------------------------------------
python, fastapi, postgresql, aws, docker, machine learning, communication

Experience
----------------------------------------
Senior Software Engineer at Google — 5 years
  • Developed backend services using python, fastapi, reducing latency by 40%.
  • 5+ years of professional experience in python.

Software Engineer at Microsoft — 3 years
  • Built microservices using docker, kubernetes, serving 10M+ daily requests.
  • 3+ years of professional experience in docker.

Education
----------------------------------------
Bachelor of Science in Computer Science, Stanford University, 2016
"""

SAMPLE_JD = """
Job Title: Senior Backend Engineer
Company: Stripe

About the Role:
We are looking for a Senior Backend Engineer to join our team.

Requirements:
Required skills: python, fastapi, postgresql, aws, docker, kubernetes, redis
5+ years of experience in software development
Education: Bachelor of Science in Computer Science or equivalent

Responsibilities:
  • Design and implement solutions using python, fastapi, postgresql
  • Collaborate with cross-functional teams
  • Write clean, maintainable, and well-tested code
"""

REQUIRED_RESULT_KEYS = [
    "ats_score",
    "skill_match_score",
    "experience_match_score",
    "education_match_score",
    "keyword_density_score",
    "formatting_score",
    "matched_skills",
    "missing_skills",
    "strengths",
    "weaknesses",
    "suggestions",
    "recommended_certifications",
]


class TestFeatureExtraction:
    """Tests for app.ml.features.extract_feature_vector."""

    def test_feature_vector_shape(self):
        """Feature vector must be a 1-D numeric array of length NUM_FEATURES."""
        vec = extract_feature_vector(SAMPLE_RESUME, SAMPLE_JD)
        assert isinstance(vec, np.ndarray), "Should return a numpy array"
        assert vec.ndim == 1, f"Expected 1-D array, got {vec.ndim}-D"
        assert vec.shape[0] == NUM_FEATURES, (
            f"Expected {NUM_FEATURES} features, got {vec.shape[0]}"
        )

    def test_feature_vector_is_numeric(self):
        """Every element must be a finite number."""
        vec = extract_feature_vector(SAMPLE_RESUME, SAMPLE_JD)
        assert np.all(np.isfinite(vec)), "All features must be finite numbers"

    def test_feature_names_match_count(self):
        """FEATURE_NAMES list must have exactly NUM_FEATURES entries."""
        assert len(FEATURE_NAMES) == NUM_FEATURES

    def test_feature_vector_deterministic(self):
        """Same inputs must produce the same feature vector."""
        vec1 = extract_feature_vector(SAMPLE_RESUME, SAMPLE_JD)
        vec2 = extract_feature_vector(SAMPLE_RESUME, SAMPLE_JD)
        np.testing.assert_array_equal(vec1, vec2)


class TestHeuristicFallback:
    """Tests that run_ats_analysis works without any saved model files.

    This path MUST pass in CI where no models have been trained.
    """

    def test_returns_valid_score_range(self):
        """ATS score must be in [0, 100]."""
        result = run_ats_analysis(SAMPLE_RESUME, SAMPLE_JD)
        assert 0 <= result["ats_score"] <= 100, (
            f"ats_score {result['ats_score']} out of range [0, 100]"
        )

    def test_all_required_keys_present(self):
        """Result dict must contain every key that AnalysisOut expects."""
        result = run_ats_analysis(SAMPLE_RESUME, SAMPLE_JD)
        for key in REQUIRED_RESULT_KEYS:
            assert key in result, f"Missing required key: {key}"

    def test_component_scores_in_range(self):
        """All component sub-scores should be in [0, 100]."""
        result = run_ats_analysis(SAMPLE_RESUME, SAMPLE_JD)
        score_keys = [
            "skill_match_score", "experience_match_score",
            "education_match_score", "keyword_density_score",
            "formatting_score",
        ]
        for key in score_keys:
            assert 0 <= result[key] <= 100, (
                f"{key} = {result[key]} out of range [0, 100]"
            )

    def test_matched_skills_are_lists(self):
        """matched_skills and missing_skills must be lists."""
        result = run_ats_analysis(SAMPLE_RESUME, SAMPLE_JD)
        assert isinstance(result["matched_skills"], list)
        assert isinstance(result["missing_skills"], list)

    def test_model_source_present(self):
        """Internal MODEL_SOURCE field must be present."""
        result = run_ats_analysis(SAMPLE_RESUME, SAMPLE_JD)
        assert "MODEL_SOURCE" in result
        assert result["MODEL_SOURCE"] in ("deep_learning", "classical_ml", "heuristic")

    def test_empty_inputs_do_not_crash(self):
        """Pipeline should handle empty strings gracefully."""
        result = run_ats_analysis("", "")
        assert 0 <= result["ats_score"] <= 100
        for key in REQUIRED_RESULT_KEYS:
            assert key in result


class TestModelLoading:
    """Conditional tests — only run if trained model files exist."""

    _SAVED_MODELS_DIR = os.path.join(
        os.path.dirname(__file__), "..", "app", "ml", "saved_models"
    )

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(
                os.path.dirname(__file__), "..", "app", "ml", "saved_models",
                "ats_score_model.joblib",
            )
        ),
        reason="Classical ML model not trained yet",
    )
    def test_classical_model_loads_and_scores(self):
        """If a classical model is present, it should load and produce a score."""
        from app.ml.pipeline import _load_classical_model

        model, meta = _load_classical_model()
        assert model is not None, "Model file exists but failed to load"
        assert isinstance(meta, dict)

        # Run full analysis — score should come from classical_ml or deep_learning
        result = run_ats_analysis(SAMPLE_RESUME, SAMPLE_JD)
        assert 0 <= result["ats_score"] <= 100

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(
                os.path.dirname(__file__), "..", "app", "ml", "saved_models",
                "ats_dl_model.pt",
            )
        ),
        reason="DL model not trained yet",
    )
    def test_dl_model_loads_and_scores(self):
        """If a DL model is present, it should load and produce a score."""
        from app.ml.pipeline import _load_dl_model

        model, meta = _load_dl_model()
        assert model is not None, "Model file exists but failed to load"
        assert isinstance(meta, dict)

        result = run_ats_analysis(SAMPLE_RESUME, SAMPLE_JD)
        assert 0 <= result["ats_score"] <= 100
