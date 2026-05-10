# ------------------------------------------------------------
# Evaluation Service
# ------------------------------------------------------------
#
# Responsibility:
# Owns answer evaluation lifecycle.
#
# Handles:
# - prompt generation
# - AI evaluation calls
# - evaluation parsing
# - evaluation persistence
# - evaluation history
#
# WHY?
# Evaluation is a distinct assessment subdomain
# inside the AI learning module.
#
# This follows:
# - Single Responsibility Principle (SRP)
# - Capability-based decomposition
# - Service-oriented architecture
# ------------------------------------------------------------

import json
import requests
import os

from app.models.user import User
from app.models.question import Question
from app.models.answer import AnswerEvaluation

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_question_for_evaluation(
    db,
    user_id: int,
    question_id: int
):
    return (
        db.query(Question)
        .filter(
            Question.question_id == question_id,
            Question.user_id == user_id
        )
        .first()
    )

def build_evaluation_prompt(
    exam: str,
    question: str,
    answer: str
):
    if exam.lower() == "upsc":
        evaluation_style = """
        - Focus on analytical depth
        - Check structure: Introduction, Body, Conclusion
        - Reward examples, facts, and multi-dimensional analysis
        - Penalize superficial answers
        """

    elif exam.lower() == "ssc":
        evaluation_style = """
        - Focus on factual accuracy
        - Keep evaluation concise and strict
        """

    else:
        evaluation_style = """
        - Focus on clarity and understanding
        """

    return f"""
    You are an expert evaluator for {exam}.

    Evaluate the answer strictly based on exam standards.

    Evaluation Guidelines:
    {evaluation_style}

    Question:
    {question}

    Answer:
    {answer}

    Return ONLY valid JSON.

    {{
      "score": 0,
      "strengths": [
        "point 1",
        "point 2"
      ],
      "improvements": [
        "point 1",
        "point 2"
      ],
      "model_answer": "ideal concise answer"
    }}
    """

def call_ai_evaluation(prompt: str):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek/deepseek-chat-v3",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        },
        timeout=20
    )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    
    except Exception:
        return """
        {
            "score": 5,
            "strengths": ["Answer submitted"],
            "improvements": ["Unable to fully evaluate"],
            "model_answer": ""
        }
        """

def parse_evaluation_response(content: str):
    try:
        # Remove markdown wrappers if present
        content = content.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        result = json.loads(content)

        return {
            "score": result.get("score", 5),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
            "model_answer": result.get("model_answer", "")
        }

    except Exception as e:
        print("Evaluation parse error:", e)

        return {
            "score": 5,
            "strengths": ["Basic attempt made"],
            "improvements": ["Improve answer structure"],
            "model_answer": content
        }

def evaluate_answer(
    db,
    user_id: int,
    question,
    answer: str
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    exam = user.exam_goal or "General Competitive Exam"

    prompt = build_evaluation_prompt(
        exam=exam,
        question=question.question_text,
        answer=answer
    )

    content = call_ai_evaluation(prompt)

    result = parse_evaluation_response(content)

    evaluation = AnswerEvaluation(
        user_id=user_id,

        question_id=question.question_id,

        question=question.question_text,
        answer=answer,

        exam=exam,
        topic=question.topic,
        difficulty=question.difficulty,

        score=result["score"],

        strengths=json.dumps(result["strengths"]),
        improvements=json.dumps(result["improvements"]),
        model_answer=result["model_answer"]
    )

    db.add(evaluation)
    db.commit()

    return result

def get_evaluation_history(
        db,
        user_id: int,
        question_id: int
):
    evaluations = (
        db.query(AnswerEvaluation).filter(
            AnswerEvaluation.user_id == user_id,
            AnswerEvaluation.question_id == question_id
        )
        .order_by(AnswerEvaluation.created_at.desc())
        .all()
    )
    return [
        {
            "answer_id": e.answer_id,
            "score": e.score,
            "answer": e.answer,

            "strengths": json.loads(e.strengths or "[]"),
            "improvements": json.loads(e.improvements or "[]"),

            "model_answer": e.model_answer,
            "created_at": e.created_at.isoformat()
        }
        for e in evaluations
    ]