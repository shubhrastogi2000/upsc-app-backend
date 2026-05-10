from pydantic import BaseModel
from typing import List


class EvaluateAnswerRequest(BaseModel):
    question_id: int
    answer: str


class EvaluateAnswerResponse(BaseModel):
    score: int
    strengths: List[str]
    improvements: List[str]
    model_answer: str