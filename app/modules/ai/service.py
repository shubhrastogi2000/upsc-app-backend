# from openai import OpenAI
import requests
import os
import json
from app.models.question import Question
from app.models.todo import Todo
from app.models.user import User
from app.models.answer import AnswerEvaluation
import unicodedata
import re

from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

#client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def clean_question_text(text: str):

    # Normalize unicode
    text = unicodedata.normalize(
        "NFKD",
        text
    )

    # Convert to safe ASCII
    text = text.encode(
        "ascii",
        "ignore"
    ).decode("ascii")

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()

def generate_and_store_questions(db, user_id: int, todo_id: int, topics: list[str]):
    result = []
    
    existing = db.query(Question).filter(
        Question.todo_id == todo_id,
        Question.user_id == user_id
    ).first()
    if existing:
        return result
    
    user = db.query(User).filter(User.id == user_id).first()
    exam = user.exam_goal
    if not exam or exam.lower() == "others":
        exam = "General Competitive Exam"

    difficulties = ["easy", "medium", "hard"]

    for topic in topics:
        
        #step 1: decide difficulty mix
        questions = []

        for diff in difficulties:
            ai_questions = generate_questions_from_ai(exam, topic, diff, count=2)  # 2 questions per difficulty

            for q in ai_questions:
                questions.append({
                    "text": q,
                    "difficulty": diff
                })
        if not questions:
            questions = [
                {"text": f"Discuss the key features of {topic}.", "difficulty": "medium"},
                {"text": f"Analyze the importance of {topic} in {exam}.", "difficulty": "medium"},
            ]
            # questions = [
            #     f"Discuss the key features of {topic}.",
            #     f"Analyze the importance of {topic} in {exam} examination.",
            #     f"What are the major challenges related to {topic}?",
            #     f"Explain {topic} with suitable examples.",
            #     f"Write a short note on {topic}.",
            #     f"How has {topic} evolved over time?",
            #     f"Critically evaluate {topic}.",
            #     f"What are the recent developments in {topic}?",
            #     f"Compare {topic} with related concepts.",
            #     f"Discuss the relevance of {topic} in current affairs."
            # ]
        
        for i, q in enumerate(questions):
            db_question = Question(
                user_id=user_id,
                todo_id=todo_id,
                topic=topic,
                question_text=q["text"],
                difficulty=q["difficulty"],   # 🔥 add this
                is_solved=False
            )
            db.add(db_question)

        result.append({
            "topic": topic,
            "questions": [q["text"] for q in questions]
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
            "question_id": q.question_id,
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

def generate_questions_from_ai(exam: str, topic: str, difficulty: str, count: int = 5):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "UPSC-App"
    }
    prompt = f"""
        Generate {count} {exam} questions on the topic: {topic}.
        
        Difficulty level: {difficulty}

        Rules: 
        - Questions should be conceptual, analytical and exam-oriented
        - Suitable for {exam} prepration
        - Keep them diverse (no repetitions)
        - Output ONLY a numbered list
        - DO NOT generate MCQ options
        - Return ONLY direct descriptive questions
    """

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print("AI API error:", response.status_code, response.text)
        return []
    result = response.json()

    try:
        content = result["choices"][0]["message"]["content"]
        # content = content.encode('utf-8', 'ignore').decode('utf-8')  # Remove non-UTF-8 characters
        #convert numbered list to array
        questions = []

        for line in content.split("\n"):
            line = line.strip()
            # 🔥 Skip empty lines
            if not line:
                continue
            # 🔥 Only accept numbered questions
            if (
                line[0].isdigit()
                and "." in line[:5]
            ):
                cleaned = (
                    line
                    .strip("1234567890. -*")
                    .replace("**", "")
                    .strip()
                )
                cleaned = clean_question_text(cleaned)
                questions.append(cleaned)
        return questions
    except Exception as e:
        print("Error parsing AI response:", e)
        return []
    
def generate_more_questions(db, user_id: int, todo_id: int):
    #step1: get todo
    todo = db.query(Todo).filter(
        Todo.todo_id == todo_id,
        Todo.user_id == user_id
    ).first()

    if not todo:
        return []
    
    topic = todo.title
    # safety limit, to prevent tons of api calls
    existing_count = db.query(Question).filter(
        Question.todo_id == todo_id,
        Question.user_id == user_id
    ).count()

    if existing_count >= 20:
        return {"error": "Question limit reached (20)"}

    #Step 2: get user exam 
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    exam = user.exam_goal
    if not exam or exam.lower() == "others":
        exam = "General Competitive Exam"

    performance = get_user_performace(db, user_id, todo_id)
    base_difficulty = get_adaptive_difficulty(performance)

    if base_difficulty == "easy":
        difficulties = ["easy", "easy", "medium"]
    elif base_difficulty == "medium":
        difficulties = ["easy", "medium", "hard"]
    else:
        difficulties = ["medium", "hard", "hard"]
    new_questions = []

    for diff in difficulties:
        ai_questions = generate_questions_from_ai(exam, topic, diff, count=2)  # 1 question per difficulty

        for q in ai_questions:
            new_questions.append({
                "text": q,
                "difficulty": diff
            })
    
    #Step 3: store in db
    for q in new_questions:
        db_question = Question(
                user_id=user_id,
                todo_id=todo_id,
                topic=topic,
                question_text=q["text"],
                difficulty=q["difficulty"],   # 🔥 add this
                is_solved=False
        )
        db.add(db_question)
    db.commit()

    return {"message": "More questions Added"}

def get_user_performace(db, user_id: int, todo_id: int):
    questions = db.query(Question).filter(
        Question.todo_id == todo_id,
        Question.user_id == user_id
    ).all()

    if not questions:
        return 0.0
    solved = sum(1 for q in questions if q.is_solved)
    total = len(questions)

    return solved/total

def get_adaptive_difficulty(performance: float):
    if performance < 0.4:
        return "easy"
    elif performance < 0.7:
        return "medium"
    else:        
        return "hard"
    
def get_topic_insights(db, user_id: int):
    questions = db.query(Question).filter(
        Question.user_id == user_id
    ).all()

    topic_map = {}

    #group by topic
    for q in questions:
        topic = q.topic
        if topic not in topic_map:
            topic_map[topic] = {"total": 0, "solved": 0}
        topic_map[topic]["total"] += 1
        if q.is_solved:
            topic_map[topic]["solved"] += 1
    result = []

    for topic, data in topic_map.items():
        total = data["total"]
        solved = data["solved"]

        performance = solved/total if total > 0 else 0.0
        if performance < 0.4:
            level = "weak"
        elif performance < 0.7:
            level = "average"
        else:
            level = "strong"
        
        result.append({
            "topic": topic,
            "performance": performance,
            "level": level
        })
    return result

# ------------------------------------------------------------
# Fetch question history for user
#
# WHY?
# Router should not directly access DB layer.
# AI service owns question domain querying.
# ------------------------------------------------------------
def get_question_history(
    db,
    user_id: int
):
    return (
        db.query(Question)
        .filter(
            Question.user_id == user_id
        )
        .all()
    )

# ------------------------------------------------------------
# Get questions for Todo
#
# Handles:
# - ownership validation
# - lazy question generation
# - question fetching
#
# WHY?
# Question lifecycle belongs to AI learning domain,
# not router layer.
# ------------------------------------------------------------
def get_or_generate_questions(
    db,
    user_id: int,
    todo_id: int
):

    # Step 1: check existing questions
    existing = (
        db.query(Question)
        .filter(
            Question.todo_id == todo_id,
            Question.user_id == user_id
        )
        .first()
    )

    # Step 2: generate if missing
    if not existing:

        todo = (
            db.query(Todo)
            .filter(
                Todo.todo_id == todo_id,
                Todo.user_id == user_id
            )
            .first()
        )

        if not todo:
            return None

        generate_and_store_questions(
            db,
            user_id,
            todo.todo_id,
            [todo.title]
        )

    # Step 3: fetch questions
    return get_questions_by_todo(
        db,
        todo_id
    )
