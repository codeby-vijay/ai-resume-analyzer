"""Synthetic training data generator for the ATS scoring model.

Produces labeled (resume_text, jd_text, ats_score_label) rows by combining
the existing skill taxonomy with templated resume/JD generation.  Labels are
derived programmatically from the *heuristic* pipeline so that the ML/DL
models learn to approximate (and eventually exceed) the hand-tuned scorer.

Usage:
    python -m app.ml.data.generate_training_data

Output:
    backend/app/ml/data/training_data.csv  (≥ 2 000 rows)
"""

from __future__ import annotations

import csv
import itertools
import os
import random
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# We import the taxonomy and the heuristic scorer so labels stay in sync with
# the hand-tuned pipeline.
# ---------------------------------------------------------------------------
from app.ml.skills_data import (
    TECHNICAL_SKILLS,
    SOFT_SKILLS,
    EDUCATION_KEYWORDS,
    EXPERIENCE_KEYWORDS,
)
from app.ml.pipeline import run_ats_analysis

SEED = 42
random.seed(SEED)

# ---------------------------------------------------------------------------
# Template building blocks
# ---------------------------------------------------------------------------

_SECTION_HEADERS_GOOD = ["Experience", "Education", "Skills", "Projects", "Certifications"]
_SECTION_HEADERS_BAD = []  # intentionally omitted for poor-formatting variants

_DEGREE_LEVELS = [
    "Bachelor of Science in Computer Science",
    "B.Tech in Information Technology",
    "Master of Science in Data Science",
    "MBA in Technology Management",
    "PhD in Artificial Intelligence",
    "Associate Degree in Software Engineering",
    "Diploma in Web Development",
]

_UNIVERSITIES = [
    "Stanford University", "MIT", "IIT Delhi", "University of Toronto",
    "Carnegie Mellon University", "Georgia Tech", "NIT Trichy",
    "University of California, Berkeley", "Harvard University",
]

_COMPANY_NAMES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix",
    "Stripe", "Uber", "Airbnb", "Salesforce", "IBM", "Infosys",
    "TCS", "Wipro", "Accenture", "Deloitte", "McKinsey",
]

_JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Data Scientist",
    "Machine Learning Engineer", "Backend Developer", "Full Stack Developer",
    "DevOps Engineer", "Cloud Architect", "Product Manager",
    "Frontend Developer", "Data Analyst", "Site Reliability Engineer",
]

_ACTION_VERBS = [
    "Developed", "Implemented", "Designed", "Built", "Architected",
    "Deployed", "Optimized", "Led", "Managed", "Created", "Automated",
    "Integrated", "Migrated", "Scaled", "Maintained", "Refactored",
]

_METRICS = [
    "reducing latency by 40%", "improving throughput by 3x",
    "serving 10M+ daily requests", "cutting costs by 25%",
    "increasing test coverage to 95%", "reducing deployment time by 60%",
    "handling 50K concurrent users", "achieving 99.9% uptime",
]


def _pick(items: list, n: int) -> list:
    """Return *n* unique random items (capped at list length)."""
    return random.sample(items, min(n, len(items)))


def _generate_resume(
    skills: List[str],
    years: int,
    degree: str | None,
    good_formatting: bool,
) -> str:
    """Build a synthetic resume string."""
    sections: List[str] = []

    # --- Header ---
    name = random.choice(["Alex Johnson", "Priya Sharma", "Jordan Lee",
                          "Sam Chen", "Maria Garcia", "Raj Patel"])
    header = f"{name}\nemail: {name.split()[0].lower()}@email.com | phone: +1-555-0{random.randint(100,999)}"
    sections.append(header)

    # --- Skills section ---
    if good_formatting:
        sections.append("\nSkills\n" + "-" * 40)
    skill_line = ", ".join(skills) if skills else "General programming"
    sections.append(skill_line)

    # --- Experience section ---
    if good_formatting:
        sections.append("\nExperience\n" + "-" * 40)
    num_roles = max(1, years // 2)
    for i in range(min(num_roles, 3)):
        company = random.choice(_COMPANY_NAMES)
        title = random.choice(_JOB_TITLES)
        role_years = max(1, years // num_roles)
        bullet_skills = _pick(skills, random.randint(1, 3)) if skills else ["software"]
        verb = random.choice(_ACTION_VERBS)
        metric = random.choice(_METRICS)
        sections.append(
            f"{title} at {company} — {role_years} years\n"
            f"  • {verb} systems using {', '.join(bullet_skills)}, {metric}.\n"
            f"  • {role_years}+ years of professional experience in {bullet_skills[0]}."
        )

    # --- Education section ---
    if good_formatting:
        sections.append("\nEducation\n" + "-" * 40)
    if degree:
        uni = random.choice(_UNIVERSITIES)
        sections.append(f"{degree}, {uni}, {2024 - years}")
    else:
        sections.append("Self-taught developer")

    # --- Formatting quality ---
    text = "\n".join(sections)
    if not good_formatting:
        # Add noise: extra special chars, remove section headers
        noise_chars = "★♦►◄●○■□▲△" * 3
        text = noise_chars + "\n" + text + "\n" + noise_chars
    return text


def _generate_jd(
    required_skills: List[str],
    years_required: int,
    degree_required: str | None,
) -> str:
    """Build a synthetic job description string."""
    title = random.choice(_JOB_TITLES)
    company = random.choice(_COMPANY_NAMES)

    lines = [
        f"Job Title: {title}",
        f"Company: {company}",
        "",
        "About the Role:",
        f"We are looking for a {title} to join our team.",
        "",
        "Requirements:",
    ]
    if required_skills:
        lines.append("Required skills: " + ", ".join(required_skills))
    if years_required > 0:
        lines.append(f"{years_required}+ years of experience in software development")
    else:
        lines.append("Entry level position, no prior experience required")
    if degree_required:
        lines.append(f"Education: {degree_required} or equivalent")
    else:
        lines.append("Education: No specific degree required")

    lines.extend([
        "",
        "Responsibilities:",
        f"  • Design and implement solutions using {', '.join(required_skills[:3]) if required_skills else 'modern technologies'}",
        f"  • Collaborate with cross-functional teams",
        f"  • Write clean, maintainable, and well-tested code",
    ])

    return "\n".join(lines)


def generate_dataset(n_rows: int = 2500) -> List[Tuple[str, str, float]]:
    """Generate *n_rows* (resume, jd, score) triples."""
    random.seed(SEED)

    all_skills = TECHNICAL_SKILLS + SOFT_SKILLS
    rows: List[Tuple[str, str, float]] = []

    # Stratified generation across multiple axes:
    #   skill_overlap_pct  ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
    #   years_required     ∈ {0, 1, 3, 5, 8}
    #   resume_years       ∈ {0, 1, 3, 5, 8, 12}
    #   education          ∈ {matched, mismatched, none}
    #   formatting         ∈ {good, bad}

    overlap_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    jd_years_options = [0, 1, 3, 5, 8]
    resume_years_options = [0, 1, 3, 5, 8, 12]
    edu_scenarios = ["match", "mismatch", "none"]
    formatting_options = [True, False]

    combos = list(itertools.product(
        overlap_levels, jd_years_options, resume_years_options,
        edu_scenarios, formatting_options,
    ))
    random.shuffle(combos)

    # We'll cycle through combos with slight randomness until we hit n_rows
    combo_cycle = itertools.cycle(combos)

    for _ in range(n_rows):
        overlap_pct, jd_years, resume_years, edu_scenario, good_fmt = next(combo_cycle)

        # Pick JD skills
        n_jd_skills = random.randint(3, 10)
        jd_skills = _pick(all_skills, n_jd_skills)

        # Determine resume skills based on overlap %
        n_overlap = max(0, int(len(jd_skills) * overlap_pct))
        overlapping = _pick(jd_skills, n_overlap)
        # Add some extra skills not in JD
        remaining_pool = [s for s in all_skills if s not in jd_skills]
        n_extra = random.randint(0, 5)
        extra = _pick(remaining_pool, n_extra)
        resume_skills = overlapping + extra

        # Education
        degree_jd = None
        degree_resume = None
        if edu_scenario == "match":
            deg = random.choice(_DEGREE_LEVELS)
            degree_jd = deg
            degree_resume = deg
        elif edu_scenario == "mismatch":
            degree_jd = random.choice(_DEGREE_LEVELS)
            degree_resume = None  # resume lacks the required degree
        # else: none — no education requirement, no education listed

        resume_text = _generate_resume(resume_skills, resume_years, degree_resume, good_fmt)
        jd_text = _generate_jd(jd_skills, jd_years, degree_jd)

        # Label = heuristic pipeline score (self-supervised)
        result = run_ats_analysis(resume_text, jd_text)
        ats_score = result["ats_score"]

        rows.append((resume_text, jd_text, ats_score))

    return rows


def main() -> None:
    print("Generating synthetic training data …")
    rows = generate_dataset(n_rows=2500)

    out_dir = Path(__file__).resolve().parent
    out_path = out_dir / "training_data.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["resume_text", "jd_text", "ats_score_label"])
        for resume, jd, score in rows:
            writer.writerow([resume, jd, score])

    print(f"✓ Saved {len(rows)} rows → {out_path}")
    print(f"  Score range: {min(r[2] for r in rows):.1f} – {max(r[2] for r in rows):.1f}")


if __name__ == "__main__":
    main()
