from pydantic import BaseModel
from typing import List, Dict, Optional

class QA(BaseModel):
    id: str
    question: str
    answer: str
    choices: Optional[List[str]] = None
    explanation: Optional[str] = None

class CreateQuizRequest(BaseModel):
    cache_id: str
    num_questions: int = 5
    seed: Optional[int] = None

class QuizQuestion(BaseModel):
    id: str
    question: str
    choices: Optional[List[str]] = None

class Quiz(BaseModel):
    id: str
    cache_id: str
    questions: List[QuizQuestion]

class QuizSubmission(BaseModel):
    answers: Dict[str, str]  # map from question id to submitted answer

class Grade(BaseModel):
    id: str
    quiz_id: str
    correct: int
    total: int
    details: Dict[str, bool]  # per-question correctness
