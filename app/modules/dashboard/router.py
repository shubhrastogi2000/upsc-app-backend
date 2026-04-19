from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.models.question import Question
from app.modules.study.service import get_today_study_time

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    total_todos = db.query(Todo).filter(Todo.user_id == user_id).count()

    completed_todos = db.query(Todo).filter(
        Todo.user_id == user_id,
        Todo.is_completed == True
    ).count()

    total_questions = db.query(Question).filter(
        Question.user_id == user_id
    ).count()

    solved_questions = db.query(Question).filter(
        Question.user_id == user_id,
        Question.is_solved == True
    ).count()

    study = get_today_study_time(db, user_id)

    return {
        "total_todos": total_todos,
        "completed_todos": completed_todos,
        "total_questions": total_questions,
        "solved_questions": solved_questions,
        "study_time_seconds": study
    }