# ------------------------------------------------------------
# Todo Router
# ------------------------------------------------------------
#
# Responsibility:
# - HTTP request handling
# - authentication dependency injection
# - request/response mapping
#
# Router should NOT contain:
# - DB queries
# - business rules
# - lifecycle orchestration
#
# WHY?
# To keep business logic centralized in service layer.
#
# This follows:
# - Separation of Concerns
# - Controller-Service architecture
# ------------------------------------------------------------


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.models.question import Question

from app.modules.todo.schema import TodoCreate
from app.modules.todo import service

router = APIRouter(prefix="/todos", tags=["Todos"])


# ✅ CREATE TODO
@router.post("/")
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.create_todo(db, current_user.id, todo.title)


# ✅ GET TODOS
@router.get("/")
def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_todos(db, current_user.id)
    # return db.query(Todo).filter(Todo.user_id == current_user.id).all()


# 🔥 MARK COMPLETE (FIXED ROUTE)
@router.put("/{todo_id}/complete")
def mark_complete(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = service.mark_complete(db, current_user.id, todo_id)

    if not todo:
        raise HTTPException(
            status_code=404,
            detail = "Todo Not Found"
        )
    return todo
    # todo = db.query(Todo).filter(
    #     Todo.todo_id == todo_id,
    #     Todo.user_id == current_user.id
    # ).first()

    # if not todo:
    #     raise HTTPException(status_code=404, detail="Todo not found")

    # todo.is_completed = True
    # db.commit()
    # db.refresh(todo)

    # return todo


# 🔥 EDIT TODO (FIXED ROUTE)
@router.put("/{todo_id}/edit")
def edit_todo(
    todo_id: int,
    title: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    updated = service.update_todo(
        db=db,
        todo_id=todo_id,
        user_id=current_user.id,
        new_title=title,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return updated
    # todo = db.query(Todo).filter(
    #     Todo.todo_id == todo_id,
    #     Todo.user_id == current_user.id
    # ).first()

    # if not todo:
    #     raise HTTPException(status_code=404, detail="Todo not found")

    # # update title
    # todo.title = title
    # db.commit()
    # db.refresh(todo)

    # # 🔥 DELETE OLD QUESTIONS
    # db.query(Question).filter(Question.todo_id == todo_id).delete()

    # # 🔥 REGENERATE QUESTIONS
    # service.generate_and_store_questions(
    #     db,
    #     current_user.id,
    #     todo.todo_id,
    #     [title]
    # )

    # return todo


# 🔥 DELETE TODO (FIXED)
@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = service.delete_todo(
        db, current_user.id, todo_id
    )
    if not result:
        raise HTTPException(
            status_code=404, detail = "Todo Not Found"
        )
    return result
    # todo = db.query(Todo).filter(
    #     Todo.todo_id == todo_id,
    #     Todo.user_id == current_user.id
    # ).first()

    # if not todo:
    #     raise HTTPException(status_code=404, detail="Todo not found")

    # # 🔥 DELETE RELATED QUESTIONS
    # db.query(Question).filter(Question.todo_id == todo_id).delete()

    # db.delete(todo)
    # db.commit()

    # return {"message": "Todo deleted"}
