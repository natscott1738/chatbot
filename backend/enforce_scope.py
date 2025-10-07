# backend/enforce_scope.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
from pathlib import Path

# Paths
BASE = Path(__file__).resolve().parent  # backend/
INDEX_DIR = BASE / "data" / "faiss_index"

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and chunks
index = faiss.read_index(str(INDEX_DIR / "index.faiss"))
with open(INDEX_DIR / "meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)
chunks = meta["chunks"]

# ---- Core functions ----
def is_cbk_related(query: str, threshold: float = 0.45) -> tuple[bool, float]:
    q = [query]
    q_emb = model.encode(q, convert_to_numpy=True, normalize_embeddings=True)
    D, I = index.search(q_emb, 1)
    score = float(D[0][0])
    return (score >= threshold, score)

def answer_cbk(query: str, k: int = 3, threshold: float = 0.55) -> str | None:
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    D, I = index.search(q_emb, k)
    if float(D[0][0]) < threshold:
        return None
    results = [chunks[i] for i in I[0]]
    return " ".join(results)

# ---- FastAPI router ----
router = APIRouter()

@router.post("/chat")
async def chat(req: Request):
    body = await req.json()
    text = body.get("text", "").strip()

    # 1) Chit-chat
    if text.lower() in {"hi", "hello", "hey"}:
        return JSONResponse({"reply": "Hello! I can help you with CBK-related questions."})

    # 2) Scope check
    in_scope, scope_score = is_cbk_related(text)
    if not in_scope:
        return JSONResponse({
            "reply": "I can only answer questions related to the Central Bank of Kenya.",
            "meta": {"scope_score": scope_score, "path": "out_of_scope"}
        })

    # 3) Retrieval
    reply = answer_cbk(text)
    if reply:
        return JSONResponse({"reply": reply, "meta": {"path": "retrieval", "scope_score": scope_score}})

    # 4) Fallback
    return JSONResponse({
        "reply": "I didn’t find a direct answer. Could you rephrase your CBK question?",
        "meta": {"path": "fallback", "scope_score": scope_score}
    })
