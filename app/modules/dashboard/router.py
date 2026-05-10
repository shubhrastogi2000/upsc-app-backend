from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.models.question import Question
from app.modules.study.service import get_today_study_time, calculate_streak
from app.modules.dashboard import service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_dashboard_data(db, current_user)