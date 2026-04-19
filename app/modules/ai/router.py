from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.modules.ai import service
from app.models.question import Question 

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/questions")
def get_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todos = (
        db.query(Todo)
        .filter(
            Todo.user_id == current_user.id,
            Todo.is_completed == False)
        .all()
    )
    topics = [t.title for t in todos]

    if not topics:
        return {"message": "No topics for today"}
    questions = service.generate_and_store_questions(db, current_user.id, topics)
    return{
        "topics": topics,
        "questions": questions
    }

@router.get("/history")
def get_question_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    questions = (
        db.query(Question)
        .filter(Question.user_id == current_user.id)
        .all()
    )

    return questions

@router.get("/questions/{todo_id}")
def get_questions(
    todo_id: int,  # ✅ type required
    db: Session = Depends(get_db),  # ✅ dependency
    current_user: User = Depends(get_current_user)  # ✅ dependency
):
    return service.get_questions_by_todo(db, todo_id)

@router.put("/questions/{question_id}/toggle")
def toggle_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.toggle_question(db, question_id, current_user.id)