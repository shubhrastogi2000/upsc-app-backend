from fastapi import APIRouter, Depends, Body
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.modules.ai import service
from app.models.question import Question 
from app.modules.ai.schema import EvaluateAnswerRequest, EvaluateAnswerResponse
from app.modules.ai import evaluation_service

router = APIRouter(prefix="/ai", tags=["AI"])

# 🔥 QUESTION HISTORY (UNCHANGED)
@router.get("/history")
def get_question_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_question_history(db, current_user.id)

# 🔥 GET QUESTIONS BY TODO (RENAMED FUNCTION)
@router.get("/questions/{todo_id}")
def get_questions_by_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    questions = (
        service.get_or_generate_questions(
            db, current_user.id, todo_id
        )
    )
    if questions is None:
        raise HTTPException(
            status_code=404,
            detail="Todo Not Found"
        )
    return questions
    
# 🔥 TOGGLE QUESTION (UNCHANGED)
@router.put("/questions/{question_id}/toggle")
def toggle_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.toggle_question(db, question_id, current_user.id)

@router.post("/questions/{todo_id}/more")
def generate_more(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.generate_more_questions(db, current_user.id, todo_id)

@router.get("/insights")
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    topics = service.get_topic_insights(db, current_user.id)

    # (Optional) future AI text insights
    ai_insights = []

    return {
        "topics": topics,          # ✅ structured
        "insights": ai_insights    # ✅ text insights
    }

@router.post(
    "/evaluate",
    response_model = EvaluateAnswerResponse
)
def evaluate(
    payload: EvaluateAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = (
        evaluation_service
        .get_question_for_evaluation(
            db,
            current_user.id,
            payload.question_id
        )
    )

    if not question:
        raise HTTPException(
            status_code=404, detail="Question not Found"
        )

    return evaluation_service.evaluate_answer(
        db = db,
        user_id = current_user.id,
        question = question,
        answer = payload.answer
    )

@router.get("/evaluations/{question_id}")
def get_evaluations(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return evaluation_service.get_evaluation_history(db, current_user.id, question_id)