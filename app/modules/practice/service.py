from app.models.question import Question

def mark_solved(db, user_id: int, question_id: int):
    question = (
        db.query(Question)
        .filter(
            Question.question_id == question_id,
            Question.user_id == user_id
        )
        .first()
    )
    if not question:
        return None
    question.is_solved = True
    db.commit()
    db.refresh(question)
    return question

def get_unsolved_questions(db, user_id: int):
    return (
        db.query(Question)
        .filter(
            Question.user_id == user_id,
            Question.is_solved == False
        )
        .all()
    )