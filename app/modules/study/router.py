from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.modules.study import service
from app.models.study_session import StudySession

router = APIRouter(prefix="/study", tags=["Study"])


@router.post("/start")
def start_study(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = service.start_session(db, current_user.id)
    if not session:
        raise HTTPException(
            status_code=400,
            detail="An active session already exists. Please stop it before starting a new one."
        )
    return {
        "session_id": session.id, 
        "start_time": session.start_time
    }


@router.post("/stop")
def stop_study(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = service.stop_session(db, current_user.id)

    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    return {"session_id": session.id, "duration_seconds": session.duration_seconds}

# ✅ TODAY TOTAL STUDY TIME
@router.get("/today")
def get_today_study(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_seconds = service.get_today_study_time(db, current_user.id)

    return {
        "total_seconds": total_seconds
    }

@router.get("/history")
def get_study_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_study_history(db, current_user.id)

    # return {
    #     "history": history
    # }

@router.get("/status")
def get_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == current_user.id,
            StudySession.end_time == None
        )
        .first()
    )

    if not session:
        return {"active": False}

    return {
        "active": True,
        "start_time": session.start_time
    }