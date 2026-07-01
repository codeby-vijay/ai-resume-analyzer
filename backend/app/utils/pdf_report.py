"""Generates a downloadable PDF analysis report using reportlab."""
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
)

from app.core.config import settings


def _score_color(score: float):
    if score >= 75:
        return colors.HexColor("#16a34a")
    if score >= 50:
        return colors.HexColor("#ca8a04")
    return colors.HexColor("#dc2626")


def generate_ats_report(analysis: dict, resume_filename: str, jd_title: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], textColor=colors.HexColor("#4f46e5"))
    heading_style = ParagraphStyle("HeadingCustom", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("AI Resume Analyzer — ATS Report", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Resume: {resume_filename}", body))
    story.append(Paragraph(f"Job Description: {jd_title or 'Untitled'}", body))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body))
    story.append(Spacer(1, 12))

    score = analysis["ats_score"]
    score_style = ParagraphStyle("Score", parent=styles["Title"], fontSize=36, textColor=_score_color(score))
    story.append(Paragraph(f"Overall ATS Score: {score:.0f} / 100", score_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Score Breakdown", heading_style))
    table_data = [["Component", "Score"]]
    components = [
        ("Skill Match", analysis["skill_match_score"]),
        ("Experience Match", analysis["experience_match_score"]),
        ("Education Match", analysis["education_match_score"]),
        ("Keyword Density", analysis["keyword_density_score"]),
        ("Formatting", analysis["formatting_score"]),
    ]
    for label, val in components:
        table_data.append([label, f"{val:.0f}/100"])

    tbl = Table(table_data, colWidths=[3 * inch, 2 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 16))

    def bullet_section(title, items):
        story.append(Paragraph(title, heading_style))
        if items:
            story.append(ListFlowable(
                [ListItem(Paragraph(item, body)) for item in items],
                bulletType="bullet",
            ))
        else:
            story.append(Paragraph("None", body))

    bullet_section("Matched Skills", analysis["matched_skills"])
    bullet_section("Missing Skills", analysis["missing_skills"])
    bullet_section("Strengths", analysis["strengths"])
    bullet_section("Weaknesses", analysis["weaknesses"])
    bullet_section("Improvement Suggestions", analysis["suggestions"])
    bullet_section("Recommended Certifications", analysis["recommended_certifications"])

    doc.build(story)
    return output_path
