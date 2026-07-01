import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.analysis import ResumeOut, JobDescriptionCreate, JobDescriptionOut
from app.ml.extraction import extract_resume_text

router = APIRouter(prefix="/api", tags=["Resumes & Job Descriptions"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/resumes/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Extract text upfront so bad files fail fast, before hitting disk/DB.
    raw_text = extract_resume_text(file.filename, contents)

    user_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(user_dir, safe_name)
    with open(filepath, "wb") as f:
        f.write(contents)

    resume = models.Resume(
        user_id=current_user.id,
        filename=file.filename,
        filepath=filepath,
        raw_text=raw_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/resumes", response_model=list[ResumeOut])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Resume)
        .filter(models.Resume.user_id == current_user.id)
        .order_by(models.Resume.uploaded_at.desc())
        .all()
    )


@router.delete("/resumes/{resume_id}", status_code=204)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if os.path.exists(resume.filepath):
        os.remove(resume.filepath)
    db.delete(resume)
    db.commit()
    return None


@router.post("/job-descriptions", response_model=JobDescriptionOut, status_code=201)
def create_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if len(payload.raw_text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Job description text is too short")

    jd = models.JobDescription(
        user_id=current_user.id,
        title=payload.title,
        raw_text=payload.raw_text,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd


@router.get("/job-descriptions", response_model=list[JobDescriptionOut])
def list_job_descriptions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.JobDescription)
        .filter(models.JobDescription.user_id == current_user.id)
        .order_by(models.JobDescription.created_at.desc())
        .all()
    )
