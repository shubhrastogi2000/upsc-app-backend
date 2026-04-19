from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

from app.modules.todo.schema import TodoCreate
from app.modules.todo import service
from app.models.todo import Todo

router = APIRouter(prefix="/todos", tags=["Todos"])

@router.post("/")
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.create_todo(db, current_user.id, todo.title)

@router.get("/")
def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # todo = service.mark_complete(db, current_user.id, todo_id)
    todo = db.query(Todo).filter(Todo.user_id == current_user.id).all()
    return todo

@router.put("/{todo_id}")
def update_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = db.query(Todo).filter(
        Todo.todo_id == todo_id,
        Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.is_completed = True
    db.commit()
    db.refresh(todo)
    return todo

@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = db.query(Todo).filter(
        Todo.todo_id == todo_id,
        Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}

@router.put("/edit/{todo_id}")
def edit_todo(
    todo_id: int,
    title: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = db.query(Todo).filter(
        Todo.todo_id == todo_id,
        Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code = 404, detail = "Todo not Found")
    
    todo.title = title
    db.commit()
    db.refresh(todo)

    return todo
