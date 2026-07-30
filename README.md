I converted this repository to run as a pywebview + Flask application instead of a React frontend.

Files added:
- main.py        -> launches Flask and opens a pywebview window
- app.py         -> Flask application with example API endpoints
- templates/index.html -> Simple HTML UI that calls the Flask API
- requirements.txt -> runtime dependencies

How to run (local):
1. Create a virtual environment and install deps:

   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt

2. Start the app:

   python main.py

A pywebview window should open showing the UI.

Notes and next steps:
- If you already have a React app, you can either:
  - Build the React app and serve the static files from Flask (put build output in `static/`), or
  - Replace the React UI with plain HTML/JS as done here.
- If you want deep integration between Python and the web view (call Python from JS), I can wire up pywebview's expose API.
- If you want me to remove React-related files or migrate an existing React codebase into this structure, point me to the files and I'll modify them.
