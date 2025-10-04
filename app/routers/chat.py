from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
from openai import OpenAI
import numpy as np
import json

# --- Router setup ---
router = APIRouter()

# --- Scope guard utility ---
CBK_KEYWORDS = [
    "central bank", "cbk", "kenya shilling", "monetary policy",
    "interest rate", "forex", "exchange rate", "treasury bond",
    "inflation", "banking supervision", "financial stability"
]

def is_cbk_related(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in CBK_KEYWORDS)

def enforce_scope(query: str):
    if not is_cbk_related(query):
        return JSONResponse(
            {"reply": "I can only answer questions related to the Central Bank of Kenya and its policies."},
            status_code=200
        )
    return None

# --- Retrieval stub (replace with your FAISS/Qdrant search) ---
def retrieve_cbk_docs(query: str, top_k: int = 3):
    """
    Load vectors + metadata and run similarity search.
    For now this is a stub returning dummy docs.
    Replace with your FAISS/Qdrant search logic.
    """
    try:
        with open("backend/data/faiss_index/meta.json") as f:
            meta = json.load(f)
        chunks = meta["chunks"]
        # TODO: run similarity search with embeddings
        # For now, just return the first few chunks
        return chunks[:top_k]
    except Exception:
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
    query = data.get("text", "")

    # 1. Scope guard
    refusal = enforce_scope(query)
    if refusal:
        return refusal

    # 2. Retrieve docs
    docs = retrieve_cbk_docs(query, top_k=3)
    if not docs:
        return {"reply": "I couldn’t find relevant CBK information for that query."}

    # 3. Build prompt
    context = "\n\n".join(docs)
    system_instruction = (
        "You are CBK Assistant. Only answer using the provided CBK documents. "
        "If the answer is not in them, say you cannot answer."
    )
    prompt = f"{system_instruction}\n\nContext:\n{context}\n\nUser: {query}\nAssistant:"

    # 4. Call model
    reply = call_model(prompt)

    # 5. Post‑check (optional)
    if "Central Bank" not in reply and "CBK" not in reply:
        return {"reply": "I can only answer questions related to the Central Bank of Kenya."}

    return {"reply": reply}
