from app.models.question import Question
from sqlalchemy import func, case
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
def get_weak_topics(db, user_id: int):
    from app.models.question import Question
    from sqlalchemy import func, case

    data = db.query(
        Question.topic,
        func.count(Question.question_id).label("total"),
        func.sum(
            case(
                (Question.is_solved == True, 1),
                else_=0
            )
        ).label("solved")
    ).filter(
        Question.user_id == user_id
    ).group_by(Question.topic).all()

    weak_topics = []

    for row in data:
        if row.total == 0:
            continue

        ratio = (row.solved or 0) / row.total

        if ratio < 0.5:
            weak_topics.append({
                "topic": row.topic,
                "progress": round(ratio * 100)
            })

    return weak_topics

def get_study_recommendations(db, user_id: int):
    from app.models.question import Question
    from sqlalchemy import func, case

    # 1. Calculate weakness
    rows = db.query(
        Question.topic,
        func.count(Question.question_id).label("total"),
        func.sum(
            case((Question.is_solved == True, 1), else_=0)
        ).label("solved")
    ).filter(
        Question.user_id == user_id
    ).group_by(Question.topic).all()

    topics = []
    for r in rows:
        if not r.total:
            continue

        ratio = (r.solved or 0) / r.total

        topics.append({
            "topic": r.topic,
            "weakness": 1 - ratio
        })

    # 2. Sort by weakest first
    topics = sorted(topics, key=lambda x: x["weakness"], reverse=True)

    # 3. Pick top 3
    suggestions = []
    for t in topics[:3]:
        suggestions.append({
            "topic": t["topic"],
            "reason": "Weak area"
        })

    return suggestions