from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    exam_goal = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    daily_goal_minutes = Column(Integer, default=120) # 2 hours per day
    