from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from app.models.study_session import StudySession

# 🔥 SINGLE SOURCE: ACTIVE SESSION
def get_active_session(db, user_id: int):
    return db.query(StudySession).filter(
        StudySession.user_id == user_id,
        StudySession.end_time == None
    ).first()


# 🔥 START SESSION (NO DUPLICATES)
def start_session(db, user_id: int):
    active_session = get_active_session(db, user_id)

    if active_session:
        return active_session  # return existing session

    session = StudySession(
        user_id=user_id,
        start_time=datetime.now(timezone.utc)
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# 🔥 STOP SESSION (ACCURATE DURATION)
def stop_session(db, user_id: int):
    session = get_active_session(db, user_id)

    if not session:
        return None

    end_time = datetime.now(timezone.utc)
    session.end_time = end_time

    # ensure timezone safe calculation
    start_time = session.start_time
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)

    duration = (end_time - start_time).total_seconds()
    session.duration_seconds = int(duration)

    db.commit()
    db.refresh(session)
    return session


# 🔥 TODAY TOTAL (ONLY ONE VERSION — CLEAN)
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

    return total_seconds


# 🔥 HISTORY
def get_study_history(db, user_id: int):
    sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id)
        .order_by(StudySession.start_time.desc())
        .all()
    )

    return [
        {
            "id": s.id,
            "start_time": s.start_time,
            "duration_seconds": s.duration_seconds or 0
        }
        for s in sessions
    ]


# 🔥 STREAK CALCULATION (FIXED TIMEZONE)
def calculate_streak(db, user_id: int, daily_goal_minutes: int):
    streak = 0
    day_offset = 0

    while True:
        day_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=day_offset)

        next_day = day_start + timedelta(days=1)

        total = db.query(func.sum(
            func.extract('epoch', StudySession.end_time - StudySession.start_time)
        )).filter(
            StudySession.user_id == user_id,
            StudySession.end_time != None,
            StudySession.start_time >= day_start,
            StudySession.start_time < next_day
        ).scalar()

        minutes = (total or 0) / 60

        if minutes >= daily_goal_minutes:
            streak += 1
            day_offset += 1
        else:
            break

    return streak

def get_weekly_study_data(db, user_id: int):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    data = []
    for i in range(6,-1,-1): # past 7 days
        day_start = today - timedelta(days=i)
        next_day = day_start + timedelta(days=1)

        sessions = db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.end_time != None,
            StudySession.start_time >= day_start,
            StudySession.start_time < next_day
        ).all()

        total_seconds = sum(s.duration_seconds for s in sessions)

        data.append({
            "date": day_start.strftime("%d %b"),
            "minutes": total_seconds // 60,
            "hours": total_seconds // 3600,
            "extra_minutes": (total_seconds % 3600) // 60,
        })

    return data