from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_user, hash_password
from app.schemas.auth import UserOut
from app.schemas.analysis import ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=UserOut)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=UserOut)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.full_name:
        current_user.full_name = payload.full_name
    if payload.password:
        current_user.hashed_password = hash_password(payload.password)
    db.commit()
    db.refresh(current_user)
    return current_user
