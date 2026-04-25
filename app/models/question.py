from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime, timezone
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # 🔥 NEW: LINK TO TODO
    todo_id = Column(Integer, ForeignKey("todos.todo_id"), nullable=False)

    topic = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    is_solved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))