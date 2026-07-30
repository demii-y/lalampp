# Quiz generator and grader

This application creates quizzes from uploaded question sources (JSON or PDF). It supports:

- Uploading a QA cache file (JSON) with questions and answers.
- Uploading a PDF and extracting Q/A pairs in two modes:
  - simple: naive text parsing (looks for Q: / A: patterns)
  - rag: optional RAG-based extraction using LangChain/OpenAI (requires API keys and additional dependencies)
- Generating randomized quizzes (each quiz can be different) and returning a quiz id
- Submitting answers and grading using the stored answer key

Quick start (local):

1. Create a virtualenv and install dependencies:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Run the app:

   uvicorn app.main:app --reload

3. Endpoints:

- POST /upload - multipart file upload (pdf or json). Returns cache_id.
- POST /quizzes - create a quiz from cache_id with body {"cache_id": "...", "num_questions": 5}
- GET /quizzes/{quiz_id} - get quiz payload
- POST /quizzes/{quiz_id}/submit - submit answers {"answers": {"q1": "A", ...}}
- GET /grades/{grade_id} - get grading result

Notes:
- If your PDF already contains Q/A in plain text with lines starting with "Q:" and "A:", use mode "simple".
- For RAG extraction, enable the optional dependencies and set OPENAI_API_KEY and other LangChain config. See processor.process_pdf_rag for details.

License: MIT
