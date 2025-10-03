import json
import numpy as np
from pathlib import Path
from typing import List, Tuple
from app.services.llm import chat_reply

BASE = Path(__file__).resolve().parents[2] / "backend" / "data" / "faiss_index"
VEC_PATH = BASE / "vectors.npy"
META_PATH = BASE / "meta.json"

def _load_index() -> Tuple[np.ndarray, List[str]]:
    if not VEC_PATH.exists() or not META_PATH.exists():
        return np.zeros((0, 1536), dtype=np.float32), []
    vecs = np.load(VEC_PATH)
    meta = json.loads(META_PATH.read_text())
    chunks = meta["chunks"]
    return vecs, chunks

def _cosine_topk(vecs: np.ndarray, query_vec: np.ndarray, k: int = 5) -> List[int]:
    # Normalize
    A = vecs
    if A.size == 0:
        return []
    A_norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-8)
    q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
    sims = A_norm @ q_norm
    idx = np.argsort(-sims)[:k]
    return idx.tolist()

def retrieve_context(query_vec: np.ndarray, k: int = 5) -> str:
    vecs, chunks = _load_index()
    idxs = _cosine_topk(vecs, query_vec, k=k)
    context = "\n\n".join(chunks[i] for i in idxs) if idxs else ""
    return context

def answer_with_retrieval(query_text: str, embed_vec: np.ndarray | None) -> tuple[str, dict]:
    context = ""
    if embed_vec is not None:
        context = retrieve_context(embed_vec, k=5)
    return chat_reply(query_text, context if context else None)
