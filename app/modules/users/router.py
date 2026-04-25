from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

from app.modules.users.schema import UserCreate, UserLogin
from app.modules.users import service

router = APIRouter(prefix="/users", tags=["Users"])


# ------------------ Create User ------------------ #
@router.post("/")
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    db_user = service.create_user(
        db=db,
        name=user.name,
        email=user.email,
        password=user.password,
        exam_goal=user.exam_goal
    )

    if not db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email
    }


# ------------------ Login ------------------ #
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    token = service.login_user(db, user.email, user.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ------------------ Get All Users ------------------ #
@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    return service.get_users(db)


# ------------------ Get Current User (Protected) ------------------ #
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "exam_goal": current_user.exam_goal
    }

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return service.create_user(
        db, 
        user.name,
        user.email,
        user.password,
        user.exam_goal
    )

@router.put("/goal")
def update_daily_goal(
    goal: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if goal <= 0:
        raise HTTPException(status_code=400, detail="Goal must be positive")

    current_user.daily_goal_minutes = goal
    db.commit()
    db.refresh(current_user)

    return {"daily_goal_minutes": current_user.daily_goal_minutes}