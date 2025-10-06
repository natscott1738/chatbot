from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import json
import numpy as np
import faiss
from openai import OpenAI

# --- Import scope guard ---
from backend.enforce_scope import enforce_scope, embed_text

# --- Router setup ---
router = APIRouter()

# --- Generic CBK fallback (used if retrieval fails) ---
GENERIC_FALLBACK = (
    "The Central Bank of Kenya (CBK) is Kenya’s monetary authority, established in 1966. "
    "It issues and manages the Kenya Shilling, formulates and implements monetary policy, "
    "regulates and supervises banks and microfinance institutions, manages foreign reserves, "
    "and ensures financial stability. CBK also manages government securities, oversees payment "
    "systems like KEPSs/RTGS, and licenses financial institutions."
)

# --- Retrieval from FAISS ---
def retrieve_cbk_docs(query: str, top_k: int = 3):
    try:
        index = faiss.read_index("backend/data/faiss_index/index.faiss")
        with open("backend/data/faiss_index/meta.json", encoding="utf-8") as f:
            meta = json.load(f)

        q_emb = embed_text(query).astype("float32")
        D, I = index.search(np.array([q_emb]), top_k)
        return [meta["chunks"][i] for i in I[0] if i < len(meta["chunks"])]
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
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()

# --- Chat endpoint ---
@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("text", "").strip()

    # 1) Scope guard (embedding-based)
    result = enforce_scope(query)
    if isinstance(result, JSONResponse):
        return result
    _, seed_fallback = result

    # 2) Try retrieval
    docs = retrieve_cbk_docs(query, top_k=3)

    # 3) If retrieval fails, return generic CBK fallback
    if not docs:
        return {"reply": GENERIC_FALLBACK}

    # 4) Build constrained prompt with retrieved context
    context = "\n\n".join(docs)
    system_instruction = (
        "You are CBK Assistant. Answer strictly using the provided CBK documents. "
        "If the answer is not in them, you must say you don't have it and then provide "
        "the generic CBK fallback content. Do not invent policies or data."
    )
    prompt = (
        f"{system_instruction}\n\n"
        f"Context:\n{context}\n\n"
        f"User: {query}\n"
        f"Assistant:"
    )

    # 5) Model call
    try:
        reply = call_model(prompt)
    except Exception as e:
        print(f"[error] Model call failed: {e}")
        return {"reply": GENERIC_FALLBACK}

    # 6) Lightweight drift check; if reply is off-topic, fallback
    if not any(token in reply.lower() for token in ["cbk", "central bank", "kenya", "treasury", "keps", "rtgs"]):
        return {"reply": GENERIC_FALLBACK}

    return {"reply": reply}
