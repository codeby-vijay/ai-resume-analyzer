from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_admin
from app.schemas.auth import UserOut

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    total_users = db.query(func.count(models.User.id)).scalar()
    total_resumes = db.query(func.count(models.Resume.id)).scalar()
    total_analyses = db.query(func.count(models.Analysis.id)).scalar()
    avg_score = db.query(func.avg(models.Analysis.ats_score)).scalar()

    return {
        "total_users": total_users or 0,
        "total_resumes": total_resumes or 0,
        "total_analyses": total_analyses or 0,
        "average_ats_score": round(avg_score, 2) if avg_score else 0,
    }


@router.put("/users/{user_id}/toggle-active", response_model=UserOut)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
    return user


@router.get("/model-info")
def get_model_info(
    _: models.User = Depends(get_current_admin),
):
    """Return which ATS scoring model is currently active and its metadata."""
    from app.ml.pipeline import get_active_model_info

    return get_active_model_info()

