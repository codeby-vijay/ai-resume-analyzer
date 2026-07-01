from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_user
from app.schemas.analysis import AnalysisOut

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=list[AnalysisOut])
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    return (
        db.query(models.Analysis)
        .filter(models.Analysis.user_id == current_user.id)
        .order_by(models.Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
