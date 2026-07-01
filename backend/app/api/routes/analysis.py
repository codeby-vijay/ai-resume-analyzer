from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_user
from app.schemas.analysis import AnalysisRequest, AnalysisOut
from app.ml.pipeline import run_ats_analysis

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisOut, status_code=201)
def analyze(
    payload: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.id == payload.resume_id, models.Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    jd = (
        db.query(models.JobDescription)
        .filter(
            models.JobDescription.id == payload.job_description_id,
            models.JobDescription.user_id == current_user.id,
        )
        .first()
    )
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    result = run_ats_analysis(resume.raw_text, jd.raw_text)

    # MODEL_SOURCE is internal metadata for logging — strip before DB insert
    model_source = result.pop("MODEL_SOURCE", "heuristic")

    analysis = models.Analysis(
        user_id=current_user.id,
        resume_id=resume.id,
        job_description_id=jd.id,
        **result,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/analyses/{analysis_id}", response_model=AnalysisOut)
def get_analysis(
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
    return analysis
