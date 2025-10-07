
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Tuple
import os
import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# Optional OpenAI summarization
USE_OPENAI = os.getenv("USE_OPENAI_SUMMARIZER", "1").strip().lower() not in ("0", "false")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if USE_OPENAI and OPENAI_API_KEY:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

# --- Router setup ---
router = APIRouter()

# --- Paths ---
# app/routers/chat.py -> parents[2] = project root
BASE = Path(__file__).resolve().parents[2]
INDEX_DIR = BASE / "backend" / "data" / "faiss_index"

# --- Load model + FAISS index once ---
# Keep model consistent with ingest_docs.py
MODEL_NAME = os.getenv("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2")
model = SentenceTransformer(MODEL_NAME)

# Load FAISS index and chunk metadata
index = faiss.read_index(str(INDEX_DIR / "index.faiss"))
with open(INDEX_DIR / "meta.json", encoding="utf-8") as f:
    meta = json.load(f)
chunks: List[str] = meta["chunks"]

# --- Retrieval parameters ---
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "3"))
RETRIEVAL_THRESHOLD = float(os.getenv("RETRIEVAL_THRESHOLD", "0.50"))  # cosine similarity on normalized vectors

# --- Helpers ---

def embed_query(text: str) -> np.ndarray:
    """Embed a single query using Sentence Transformers and return normalized numpy vector."""
    q_emb = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return q_emb.astype(np.float32)

def retrieve_cbk_docs(query: str, top_k: int = RETRIEVAL_TOP_K, threshold: float = RETRIEVAL_THRESHOLD) -> Tuple[List[str], List[float]]:
    """
    Search FAISS for top_k chunks. Returns (chunks, scores).
    Empty list if best score is below threshold.
    """
    try:
        q_emb = embed_query(query)
        D, I = index.search(q_emb, top_k)
        scores = [float(s) for s in D[0]]
        ids = [int(i) for i in I[0]]

        # Reject if top-1 score below threshold
        if not scores or scores[0] < threshold:
            return [], []

        results = [chunks[i] for i in ids if 0 <= i < len(chunks)]
        return results, scores
    except Exception as e:
        print(f"[warn] Retrieval failed: {e}")
        return [], []

def build_prompt(query: str, docs: List[str]) -> str:
    """
    Build a grounded prompt for the summarizer. Keep concise, forbid invention.
    """
    context = "\n\n".join(docs)
    system_instruction = (
        "You are CBK Assistant. Answer the user's question strictly using the provided CBK documents. "
        "Be concise, precise, and factual. If the answer is not present in the documents, say you do not have it. "
        "Do not invent policies or data. Use Kenyan/CBK terminology where appropriate."
    )
    prompt = (
        f"{system_instruction}\n\n"
        f"Context:\n{context}\n\n"
        f"User question:\n{query}\n\n"
        f"Assistant concise answer:"
    )
    return prompt

def summarize_answer_with_openai(prompt: str) -> str:
    """
    Summarize using OpenAI if configured. Falls back to local summarizer on error.
    """
    if not openai_client:
        return ""

    try:
        resp = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_SUMMARIZER_MODEL", "gpt-4o-mini"),
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[error] OpenAI summarization failed: {e}")
        return ""

def local_summarize(query: str, docs: List[str], max_sentences: int = 5) -> str:
    """
    Lightweight extractive summarizer:
    - Split top retrieved doc(s) into sentences.
    - Rank sentences by keyword overlap with the query.
    - Return the top-k sentences as a concise answer.
    This avoids any hard-coded snippets while staying local.
    """
    import re

    text = "\n\n".join(docs)
    # Simple sentence split
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences:
        return "I do not have that information in the provided CBK documents."

    q_tokens = set(re.findall(r"\w+", query.lower()))
    def score_sentence(s: str) -> int:
        s_tokens = set(re.findall(r"\w+", s.lower()))
        return len(q_tokens & s_tokens)

    ranked = sorted(sentences, key=score_sentence, reverse=True)
    summary = " ".join(ranked[:max_sentences]).strip()
    # Guard against empty or overly long output
    if not summary:
        return "I do not have that information in the provided CBK documents."
    return summary[:2000]  # keep it reasonable

# --- Chat endpoint ---

@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("text", "").strip()

    # 1) Chit-chat
    if query.lower() in {"hi", "hello", "hey"}:
        return {"reply": "Hello! I can help you with CBK-related questions."}

    # 2) Retrieval
    docs, scores = retrieve_cbk_docs(query)

    # 3) Out-of-scope handling (no relevant CBK chunks found)
    if not docs:
        return {"reply": "I can only answer questions related to the Central Bank of Kenya."}

    # 4) Build grounded prompt
    prompt = build_prompt(query, docs)

    # 5) Summarize (OpenAI if available; else local extractive summarization)
    reply = ""
    if USE_OPENAI and openai_client:
        reply = summarize_answer_with_openai(prompt)

    if not reply:
        reply = local_summarize(query, docs)

    # 6) Return concise answer with minimal meta for tuning
    return {
        "reply": reply,
        "meta": {
            "top_scores": scores,
            "top_k_used": len(docs),
            "summarizer": "openai" if (USE_OPENAI and openai_client) else "local_extractive",
            "model": MODEL_NAME,
        },
    }
