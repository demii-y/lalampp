from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import shutil
import os
from . import processor, storage, models

app = FastAPI(title="Quiz Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
CACHE_DIR = os.path.join(os.getcwd(), "cache")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

@app.post("/upload")
async def upload(file: UploadFile = File(...), mode: str = "simple"):
    """Upload a JSON QA cache or a PDF to extract Q&A pairs.
    mode: 'simple' or 'rag' (rag requires optional deps and API keys)
    """
    filename = f"{uuid4().hex}_{file.filename}"
    dest = os.path.join(UPLOAD_DIR, filename)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.lower().endswith(".json"):
        # store directly as cache
        cache_id = storage.save_cache_from_json(dest)
        return {"cache_id": cache_id}

    if file.filename.lower().endswith(".pdf"):
        if mode == "simple":
            qas = processor.process_pdf_simple(dest)
        elif mode == "rag":
            qas = processor.process_pdf_rag(dest)
        else:
            raise HTTPException(status_code=400, detail="mode must be 'simple' or 'rag'")
        if not qas:
            raise HTTPException(status_code=400, detail="No Q/A pairs found in the document.")
        cache_id = storage.save_cache(qas, source=file.filename)
        return {"cache_id": cache_id}

    raise HTTPException(status_code=400, detail="Unsupported file type; upload a .json or .pdf file")

@app.post("/quizzes")
def create_quiz(payload: models.CreateQuizRequest):
    cache = storage.load_cache(payload.cache_id)
    if cache is None:
        raise HTTPException(status_code=404, detail="cache_id not found")
    quiz = storage.make_quiz_from_cache(cache, payload.num_questions, seed=payload.seed)
    return quiz

@app.get("/quizzes/{quiz_id}")
def get_quiz(quiz_id: str):
    quiz = storage.load_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="quiz not found")
    return quiz

@app.post("/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission: models.QuizSubmission):
    quiz = storage.load_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="quiz not found")
    grade = storage.grade_quiz(quiz, submission.answers)
    return grade

@app.get("/grades/{grade_id}")
def get_grade(grade_id: str):
    grade = storage.load_grade(grade_id)
    if grade is None:
        raise HTTPException(status_code=404, detail="grade not found")
    return grade
