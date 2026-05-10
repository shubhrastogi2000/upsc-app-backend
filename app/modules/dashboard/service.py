from sqlalchemy.orm import Session

from app.models.todo import Todo
from app.models.question import Question

from app.modules.study.service import (
    get_today_study_time,
    calculate_streak,
)


# /// ------------------------------------------------------------
# /// Dashboard Service
# /// ------------------------------------------------------------
# ///
# /// Purpose:
# /// Owns dashboard aggregation workflow.
# ///
# /// Owns:
# /// - dashboard statistics
# /// - progress aggregation
# /// - study analytics coordination
# /// - streak calculation orchestration
# ///
# /// IMPORTANT:
# /// Router should NOT:
# /// - aggregate DB queries
# /// - calculate analytics
# /// - orchestrate workflows
# ///
# /// WHY?
# /// Separates:
# /// - HTTP coordination
# /// from:
# /// - business aggregation logic
# ///
# /// Benefits:
# /// - cleaner router
# /// - scalable backend architecture
# /// - reusable aggregation workflows
# /// - easier testing
# /// ------------------------------------------------------------
def get_dashboard_data(
    db: Session,
    current_user,
):

    user_id = current_user.id

    total_todos = (
        db.query(Todo)
        .filter(
            Todo.user_id == user_id
        )
        .count()
    )

    completed_todos = (
        db.query(Todo)
        .filter(
            Todo.user_id == user_id,
            Todo.is_completed == True,
        )
        .count()
    )

    total_questions = (
        db.query(Question)
        .filter(
            Question.user_id == user_id
        )
        .count()
    )

    solved_questions = (
        db.query(Question)
        .filter(
            Question.user_id == user_id,
            Question.is_solved == True,
        )
        .count()
    )

    today_seconds = (
        get_today_study_time(
            db,
            user_id,
        )
    )

    today_minutes = (
        today_seconds // 60
    )

    streak = calculate_streak(
        db,
        user_id,
        current_user.daily_goal_minutes,
    )

    return {

        "total_todos":
            total_todos,

        "completed_todos":
            completed_todos,

        "total_questions":
            total_questions,

        "solved_questions":
            solved_questions,

        "study_time_seconds":
            today_seconds,

        "today_progress_minutes":
            today_minutes,

        "daily_goal_minutes":
            current_user.daily_goal_minutes,

        "streak_days":
            streak,

        "exam":
            current_user.exam_goal,
    }