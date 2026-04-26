from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    exam_goal: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoalUpdate(BaseModel):
    exam_goal: str
    daily_goal_minutes: int