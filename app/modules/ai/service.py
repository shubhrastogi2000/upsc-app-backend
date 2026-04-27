# from openai import OpenAI
import os
from app.models.question import Question
from app.models.todo import Todo
from app.models.user import User

#client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def generate_and_store_questions(db, user_id: int, todo_id: int, topics: list[str]):
    result = []
    
    existing = db.query(Question).filter(
        Question.todo_id == todo_id,
        Question.user_id == user_id
    ).first()
    if existing:
        return result
    
    user = db.query(User).filter(User.id == user_id).first()
    exam = user.exam_goal or "General"
    difficulties = ["easy", "medium", "hard"]

    for topic in topics:
        questions = [
            f"Discuss the key features of {topic}.",
            f"Analyze the importance of {topic} in {exam} examination.",
            f"What are the major challenges related to {topic}?",
            f"Explain {topic} with suitable examples.",
            f"Write a short note on {topic}.",
            f"How has {topic} evolved over time?",
            f"Critically evaluate {topic}.",
            f"What are the recent developments in {topic}?",
            f"Compare {topic} with related concepts.",
            f"Discuss the relevance of {topic} in current affairs."
        ]
        
        for i, q in enumerate(questions):
            db_question = Question(
                user_id=user_id,
                todo_id=todo_id,
                topic=topic,
                question_text=q,
                difficulty=difficulties[i % 3],   # 🔥 add this
                is_solved=False
            )
            db.add(db_question)

        result.append({
            "topic": topic,
            "questions": questions
        })

    db.commit()

    return result

def get_questions_by_todo(db, todo_id: int):
    # 🔹 Step 1: get todo title
    todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()

    if not todo:
        return []

    # 🔹 Step 2: fetch questions using topic match
    questions = db.query(Question).filter(
        Question.todo_id == todo_id,
        Question.user_id == todo.user_id
    ).all()

    # 🔹 Step 3: return clean response
    return [
        {
            "id": q.question_id,
            "question": q.question_text,
            "is_solved": q.is_solved,
            "difficulty": q.difficulty 
        }
        for q in questions
    ]

def toggle_question(db, question_id: int, user_id: int):
    question = db.query(Question).filter(
        Question.question_id == question_id,
        Question.user_id == user_id
    ).first()

    if not question:
        return {"error": "Question not found"}

    # 🔥 Toggle logic
    question.is_solved = not question.is_solved

    db.commit()
    db.refresh(question)

    return {
        "id": question.question_id,
        "is_solved": question.is_solved
    }

    # prompt = f"""
    # Generate 5 UPSC-style questions for each topic:
    
    # Topics:
    # {', '.join(topics)}

    # Keep questions conceptual and exam-oriented.
    # """
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "user", "content":prompt}
    #     ]
    # )
    # return response.choices[0].message.content
