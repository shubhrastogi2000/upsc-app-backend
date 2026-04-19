from app.models.question import Question
from app.models.study_session import StudySession
from datetime import datetime, timezone

def get_summary(db, user_id: int):
    #Questions 
    total_questions = db.query(Question).filter(
        Question.user_id == user_id
    ).count()

    solved_questions = db.query(Question).filter(
        Question.user_id == user_id,
        Question.is_solved == True
    ).count()

    unsolved_questions = total_questions - solved_questions

    completion_percentage = (
        (solved_questions / total_questions) * 100
        if total_questions > 0 else 0
    )

    #Study tinme (today)
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    sessions = db.query(StudySession).filter(
        StudySession.user_id == user_id,
        StudySession.start_time >= start_of_day,
        StudySession.duration_seconds != None
    ).all()

    total_seconds = sum(s.duration_seconds for s in sessions)

    return {
        "total_questions": total_questions,
        "solved_questions": solved_questions,
        "unsolved_questions": unsolved_questions,
        "completion_percentage": round(completion_percentage, 2),
        "today_study_minutes_seconds": total_seconds // 60
    }