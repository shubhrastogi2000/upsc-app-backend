from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.modules.ai import service
from app.models.question import Question 

router = APIRouter(prefix="/ai", tags=["AI"])


# 🔥 GENERATE QUESTIONS FOR ALL TODOS (FIXED)
# @router.get("/questions")
# def generate_questions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     todos = (
#         db.query(Todo)
#         .filter(
#             Todo.user_id == current_user.id,
#             Todo.is_completed == False
#         )
#         .all()
#     )

#     if not todos:
#         return {"message": "No topics for today"}

#     result = []

#     # 🔥 FIX: generate per todo (IMPORTANT)
#     for todo in todos:
#         questions = service.generate_and_store_questions(
#             db,
#             current_user.id,
#             todo.id,            # ✅ PASS TODO ID
#             [todo.title]        # topic list
#         )

#         result.append({
#             "todo_id": todo.id,
#             "topic": todo.title,
#             "questions": questions
#         })

#     return {"data": result}


# 🔥 QUESTION HISTORY (UNCHANGED)
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


# 🔥 GET QUESTIONS BY TODO (RENAMED FUNCTION)
@router.get("/questions/{todo_id}")
def get_questions_by_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 🔹 Step 1: check if questions already exist
    existing = db.query(Question).filter(
        Question.todo_id == todo_id,
        Question.user_id == current_user.id
    ).first()

    # 🔹 Step 2: if NOT → generate
    if not existing:
        todo = db.query(Todo).filter(
            Todo.todo_id == todo_id,
            Todo.user_id == current_user.id
        ).first()

        if not todo:
            return {"error": "Todo not found"}

        service.generate_and_store_questions(
            db,
            current_user.id,
            todo.todo_id,
            [todo.title]
        )

    # 🔹 Step 3: fetch questions
    return service.get_questions_by_todo(db, todo_id)

# 🔥 TOGGLE QUESTION (UNCHANGED)
@router.put("/questions/{question_id}/toggle")
def toggle_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.toggle_question(db, question_id, current_user.id)
