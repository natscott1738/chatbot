from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import json
import numpy as np
from openai import OpenAI

# --- Import the scope guard ---
from backend.enforce_scope import enforce_scope

# --- Router setup ---
router = APIRouter()

# --- Retrieval stub (replace with FAISS/Qdrant search) ---
def retrieve_cbk_docs(query: str, top_k: int = 3):
    """
    Load vectors + metadata and run similarity search.
    For now this is a stub returning dummy docs.
    Replace with your FAISS/Qdrant search logic.
    """
    try:
        with open("backend/data/faiss_index/meta.json", encoding="utf-8") as f:
            meta = json.load(f)
        chunks = meta["chunks"]
        # TODO: run similarity search with embeddings
        return chunks[:top_k]
    except Exception as e:
        print(f"[warn] Retrieval failed: {e}")
        return []

# --- Model call wrapper ---
def call_model(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # or whichever chat model you use
        messages=[{"role": "system", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()

# --- Chat endpoint ---
@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("text", "").strip()

    # 1. Scope guard
    result = enforce_scope(query)
    if isinstance(result, JSONResponse):
        # Out-of-scope or chit-chat handled directly
        return result
    scope_response, seed_fallback = result  # unpack tuple

    # 2. Retrieve docs
    docs = retrieve_cbk_docs(query, top_k=3)

    # 3. If retrieval fails, use seed fallback
    if not docs:
        return {"reply": seed_fallback}

    # 4. Build prompt
    context = "\n\n".join(docs)
    system_instruction = (
        "You are CBK Assistant. Only answer using the provided CBK documents. "
        "If the answer is not in them, fall back to the seed knowledge."
    )
    prompt = f"{system_instruction}\n\nContext:\n{context}\n\nUser: {query}\nAssistant:"

    # 5. Call model
    reply = call_model(prompt)

    # 6. Post-check: if model drifts, use fallback
    if "Central Bank" not in reply and "CBK" not in reply:
        return {"reply": seed_fallback}

    return {"reply": reply}
