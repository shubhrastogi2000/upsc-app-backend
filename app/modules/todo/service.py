# ------------------------------------------------------------
# Todo Service
# ------------------------------------------------------------
#
# Responsibility:
# Owns Todo business lifecycle and orchestration.
#
# Handles:
# - todo CRUD
# - question lifecycle management
# - aggregate ownership rules
# - regeneration flows
#
# WHY?
# Todo acts as the aggregate root for Questions.
#
# This follows:
# - Separation of Concerns
# - Aggregate Ownership
# - Service-Oriented Architecture
# ------------------------------------------------------------

from app.models.todo import Todo
from app.models.question import Question
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.question import Question
from app.modules.ai import service as ai_service
from app.modules.ai.service import generate_and_store_questions

# 🔥 CREATE TODO (FIXED)
def create_todo(db: Session, user_id: int, title: str):
    todo = Todo(
        user_id=user_id,
        title=title
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    # 🔥 USE todo.todo_id
    # generate_and_store_questions(
    #     db,
    #     user_id,
    #     todo.todo_id,   # ✅ CORRECT
    #     [title]
    # )

    return todo


# 🔥 GET TODOS
def get_todos(db: Session, user_id: int):
    return db.query(Todo).filter(Todo.user_id == user_id).all()


# 🔥 MARK COMPLETE (FIXED)
def mark_complete(db, user_id: int, todo_id: int):
    todo = (
        db.query(Todo)
        .filter(Todo.user_id == user_id, Todo.todo_id == todo_id)
        .first()
    )

    if not todo:
        return None

    todo.is_completed = True
    db.commit()
    db.refresh(todo)

    return todo


# 🔥 DELETE TODO (IMPORTANT)
def delete_todo(db, user_id: int, todo_id: int):
    todo = (
        db.query(Todo)
        .filter(Todo.user_id == user_id, Todo.todo_id == todo_id)
        .first()
    )

    if not todo:
        return None

    # 🔥 DELETE RELATED QUESTIONS
    db.query(Question).filter(Question.todo_id == todo_id).delete()

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted"}


# 🔥 UPDATE TODO (IMPORTANT)
def update_todo(
    db: Session,
    todo_id: int,
    user_id: int,
    new_title: str,
):

    todo = (
        db.query(Todo)
        .filter(
            Todo.todo_id == todo_id,
            Todo.user_id == user_id
        )
        .first()
    )

    if not todo:
        return None

    # 🔥 Update title
    todo.title = new_title

    # 🔥 Remove old generated questions
    (
        db.query(Question)
        .filter(
            Question.todo_id == todo_id,
            Question.user_id == user_id
        )
        .delete()
    )

    db.commit()

    # 🔥 Generate fresh questions
    ai_service.generate_and_store_questions(
        db=db,
        user_id=user_id,
        todo_id=todo.todo_id,
        topics=[new_title],
    )

    db.refresh(todo)

    return todo