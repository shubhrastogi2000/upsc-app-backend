from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

from app.modules.analytics import service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_summary(db, current_user.id)

@router.get("/weak-topics")
def get_weak_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_weak_topics(db, current_user.id)

@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_study_recommendations(db, current_user.id)