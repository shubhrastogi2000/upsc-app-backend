from datetime import datetime, timezone
from app.models.study_session import StudySession


def start_session(db, user_id: int):
    active_session = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == user_id,
            StudySession.end_time == None
        )
        .first()
    )

    if active_session:
        return None

    session = StudySession(
        user_id=user_id,
        start_time=datetime.now(timezone.utc)
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def stop_session(db, user_id: int):
    session = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == user_id,
            StudySession.end_time == None
        )
        .order_by(StudySession.start_time.desc())
        .first()
    )

    if not session:
        return None

    end_time = datetime.now(timezone.utc)
    session.end_time = end_time

    # Ensure timezone consistency
    start_time = session.start_time
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)

    duration = (end_time - start_time).total_seconds()
    session.duration_seconds = int(duration)

    db.commit()
    db.refresh(session)
    return session


# ✅ FIXED VERSION
def get_today_study_time(db, user_id: int):
    now = datetime.now(timezone.utc)

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    sessions = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == user_id,
            StudySession.start_time >= start_of_day,
            StudySession.duration_seconds != None
        )
        .all()
    )

    total_seconds = sum(s.duration_seconds for s in sessions)

    return total_seconds  # ✅ RETURN ONLY INT

def get_study_history(db, user_id: int):
    sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id)
        .order_by(StudySession.start_time.desc())
        .all()
    )

    result = []

    for s in sessions:
        result.append({
            "id": s.id,
            "start_time": s.start_time,
            "duration_seconds": s.duration_seconds or 0
        })

    return result