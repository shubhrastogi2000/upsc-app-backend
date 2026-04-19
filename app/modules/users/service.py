from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
from app.core.security import verify_password, create_access_token

def create_user(db: Session, name: str, email: str, password: str, exam_goal: str | None):
    hashed_password = hash_password(password)
    db_user = User(
        name = name,
        email = email,
        password_hash = hashed_password,
        exam_goal = exam_goal
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Email already registered")

def get_users(db: Session):
    return db.query(User).all()

def login_user(db, email: str, password: str):
    user = db.query(User).filter(User.email==email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    token = create_access_token(data={"sub": user.email})
    return token

