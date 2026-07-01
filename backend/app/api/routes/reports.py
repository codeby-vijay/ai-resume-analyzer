import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_user
from app.core.config import settings
from app.utils.pdf_report import generate_ats_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{analysis_id}")
def get_report(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    analysis = (
        db.query(models.Analysis)
        .filter(models.Analysis.id == analysis_id, models.Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    existing_report = (
        db.query(models.Report).filter(models.Report.analysis_id == analysis.id).first()
    )
    if existing_report and os.path.exists(existing_report.filepath):
        return FileResponse(
            existing_report.filepath,
            media_type="application/pdf",
            filename=f"ats_report_{analysis.id}.pdf",
        )

    analysis_dict = {
        "ats_score": analysis.ats_score,
        "skill_match_score": analysis.skill_match_score,
        "experience_match_score": analysis.experience_match_score,
        "education_match_score": analysis.education_match_score,
        "keyword_density_score": analysis.keyword_density_score,
        "formatting_score": analysis.formatting_score,
        "matched_skills": analysis.matched_skills,
        "missing_skills": analysis.missing_skills,
        "strengths": analysis.strengths,
        "weaknesses": analysis.weaknesses,
        "suggestions": analysis.suggestions,
        "recommended_certifications": analysis.recommended_certifications,
    }

    reports_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id), "reports")
    output_path = os.path.join(reports_dir, f"ats_report_{analysis.id}.pdf")
    generate_ats_report(
        analysis_dict,
        resume_filename=analysis.resume.filename,
        jd_title=analysis.job_description.title,
        output_path=output_path,
    )

    if not existing_report:
        report = models.Report(analysis_id=analysis.id, filepath=output_path)
        db.add(report)
        db.commit()

    return FileResponse(
        output_path, media_type="application/pdf", filename=f"ats_report_{analysis.id}.pdf"
    )
