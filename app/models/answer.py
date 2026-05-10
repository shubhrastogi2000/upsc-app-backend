from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from datetime import datetime, timezone
from app.core.database import Base


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    answer_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    question_id = Column(
        Integer,
        ForeignKey("questions.question_id"),
        nullable=True
    )

    # Snapshot fields
    question = Column(Text)
    answer = Column(Text)

    exam = Column(String)
    topic = Column(String)
    difficulty = Column(String)

    # AI evaluation
    score = Column(Integer)

    strengths = Column(Text)
    improvements = Column(Text)
    model_answer = Column(Text)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))