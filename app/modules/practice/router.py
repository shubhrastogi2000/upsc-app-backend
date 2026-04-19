from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

from app.modules.practice import service

router = APIRouter(prefix="/practice", tags=["Practice"])

@router.get("/solve/{question_id}")
def solve_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = service.mark_solved(db, current_user.id, question_id)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Marked as solved"}

@router.get("/unsolved")
def get_unsolved(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_unsolved_questions(db, current_user.id)
