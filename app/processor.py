import re
from typing import List, Dict
from PyPDF2 import PdfReader
import os


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    full = []
    for p in reader.pages:
        try:
            txt = p.extract_text() or ""
        except Exception:
            txt = ""
        full.append(txt)
    return "\n".join(full)


def process_pdf_simple(path: str) -> List[Dict]:
    """A simple heuristic parser that looks for lines starting with Q: and A:.
    It returns a list of {'id','question','answer','choices'} objects.
    """
    text = extract_text_from_pdf(path)
    # Normalize line breaks
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    qas = []
    q = None
    a = None
    idx = 0
    for line in lines:
        if re.match(r"^Q[:\.]", line, re.I) or line.lower().startswith("question"):
            if q and a:
                idx += 1
                qas.append({"id": f"q{idx}", "question": q, "answer": a})
                q = None
                a = None
            # remove leading Q: or Question
            q = re.sub(r"^Q[:\.]\s*|^Question[:\.]?\s*", "", line, flags=re.I)
        elif re.match(r"^A[:\.]", line, re.I) or line.lower().startswith("answer"):
            a = re.sub(r"^A[:\.]\s*|^Answer[:\.]?\s*", "", line, flags=re.I)
        else:
            # continuation lines
            if a is None and q is not None:
                q += " " + line
            elif a is not None:
                a += " " + line
    if q and a:
        idx += 1
        qas.append({"id": f"q{idx}", "question": q, "answer": a})
    return qas


def process_pdf_rag(path: str) -> List[Dict]:
    """Placeholder for RAG-based processing.
    This function will run if langchain and OpenAI are installed and configured.
    It will:
      - split the document into chunks
      - build embeddings
      - run a prompt to generate Q/A pairs from the content

    If optional dependencies are not available, it raises RuntimeError.
    """
    try:
        from langchain.text_splitter import CharacterTextSplitter
        from langchain.document_loaders import TextLoader
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.llms import OpenAI
    except Exception as e:
        raise RuntimeError("RAG mode requires langchain, openai, and faiss-cpu packages. Install optional deps and set OPENAI_API_KEY.")

    text = extract_text_from_pdf(path)
    splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    chunks = splitter.split_text(text)
    # build embeddings
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(chunks, embeddings)
    llm = OpenAI(temperature=0)

    qas = []
    # For each top chunk run a Q/A generator prompt (simple approach)
    for i, chunk in enumerate(chunks[:10]):
        prompt = f"From the following text, create up to 3 clear question-and-answer pairs suitable for a quiz. Respond in JSON array of objects with fields question and answer. Text:\n\n{chunk}"
        resp = llm(prompt)
        # try to find JSON in resp
        import json
        try:
            data = json.loads(resp)
        except Exception:
            # fallback: naive parse lines like Q: ... A: ...
            data = []
            lines = [l.strip() for l in resp.splitlines() if l.strip()]
            q = None
            a = None
            for line in lines:
                if re.match(r"^Q[:\.]", line, re.I) or line.lower().startswith("question"):
                    q = re.sub(r"^Q[:\.]\s*|^Question[:\.]?\s*", "", line, flags=re.I)
                elif re.match(r"^A[:\.]", line, re.I) or line.lower().startswith("answer"):
                    a = re.sub(r"^A[:\.]\s*|^Answer[:\.]?\s*", "", line, flags=re.I)
                else:
                    if q is not None and a is None:
                        q += " " + line
                    elif a is not None:
                        a += " " + line
                if q and a:
                    data.append({"question": q, "answer": a})
                    q = None
                    a = None
        for qa in data:
            qas.append({"id": f"q{len(qas)+1}", "question": qa.get("question"), "answer": qa.get("answer")})
    return qas
