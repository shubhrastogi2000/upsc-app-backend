from app.models.todo import Todo
from app.models.question import Question
from datetime import datetime, timezone

from app.modules.ai.service import generate_and_store_questions

def create_todo(db, user_id: int, title: str):
    todo = Todo(
        user_id = user_id,
        title = title
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    generate_and_store_questions(db, user_id, [title])
    return todo

def get_todos(db, user_id: int):
    return db.query(Todo).filter(Todo.user_id == user_id).all()

def mark_complete(db, user_id: int, todo_id: int):
    todo = (
        db.query(Todo)
        .filter(Todo.user_id==user_id, Todo.todo_id==todo_id)
        .first()
    )
    if not todo:
        return None
    todo.is_completed = True
    db.commit()
    db.refresh(todo)
    return todo

