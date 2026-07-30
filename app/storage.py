import json
import os
from uuid import uuid4
from typing import List, Dict, Any
from .models import QA, Quiz, QuizQuestion, Grade
import random

CACHE_DIR = os.path.join(os.getcwd(), "cache")
QUIZ_DIR = os.path.join(os.getcwd(), "quizzes")
GRADE_DIR = os.path.join(os.getcwd(), "grades")
for d in (CACHE_DIR, QUIZ_DIR, GRADE_DIR):
    os.makedirs(d, exist_ok=True)


def save_cache(qas: List[Dict[str, Any]], source: str = None) -> str:
    cache_id = uuid4().hex
    obj = {"id": cache_id, "source": source, "qas": qas}
    path = os.path.join(CACHE_DIR, f"{cache_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return cache_id


def save_cache_from_json(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        obj = json.load(f)
    # Expecting either {qas: [...]} or a list of qas
    if isinstance(obj, dict) and "qas" in obj:
        qas = obj["qas"]
    elif isinstance(obj, list):
        qas = obj
    else:
        raise ValueError("JSON must be a list of Q/A or an object with 'qas' key")
    # normalize ids
    for i, q in enumerate(qas):
        if "id" not in q:
            q["id"] = f"q{i+1}"
    return save_cache(qas)


def load_cache(cache_id: str):
    path = os.path.join(CACHE_DIR, f"{cache_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_quiz_from_cache(cache: Dict, num_questions: int = 5, seed: int = None) -> Dict:
    qas = cache.get("qas", [])
    if seed is not None:
        random.seed(seed)
    selected = random.sample(qas, min(num_questions, len(qas)))
    quiz_id = uuid4().hex
    questions = ["" for _ in selected]
    quiz_questions = []
    for q in selected:
        qq = QuizQuestion(id=q.get("id"), question=q.get("question"), choices=q.get("choices"))
        quiz_questions.append(qq.dict())
    quiz = {"id": quiz_id, "cache_id": cache.get("id"), "questions": quiz_questions}
    path = os.path.join(QUIZ_DIR, f"{quiz_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(quiz, f, ensure_ascii=False, indent=2)
    return quiz


def load_quiz(quiz_id: str):
    path = os.path.join(QUIZ_DIR, f"{quiz_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def grade_quiz(quiz: Dict, submitted_answers: Dict[str, str]) -> Dict:
    cache = load_cache(quiz.get("cache_id"))
    id_to_answer = {q["id"]: q["answer"] for q in cache.get("qas", [])}
    details = {}
    correct = 0
    total = len(quiz.get("questions", []))
    for q in quiz.get("questions", []):
        qid = q["id"]
        correct_answer = id_to_answer.get(qid)
        submitted = submitted_answers.get(qid)
        ok = False
        if submitted is not None and correct_answer is not None:
            ok = str(submitted).strip().lower() == str(correct_answer).strip().lower()
        details[qid] = ok
        if ok:
            correct += 1
    grade_id = uuid4().hex
    result = {"id": grade_id, "quiz_id": quiz.get("id"), "correct": correct, "total": total, "details": details}
    with open(os.path.join(GRADE_DIR, f"{grade_id}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def load_grade(grade_id: str):
    path = os.path.join(GRADE_DIR, f"{grade_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
