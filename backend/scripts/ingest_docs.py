# backend/scripts/ingest_docs.py
import os
import json
import faiss
import time
import numpy as np
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Optional local sentence-transformers backend
USE_LOCAL = os.getenv("USE_LOCAL_EMBEDDINGS", "1").strip() not in ("0", "false", "False")
EMBED_MODEL_LOCAL = os.getenv("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2")

# OpenAI-related defaults (only used if USE_LOCAL is false)
EMBED_MODEL_OPENAI = os.getenv("EMBED_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Load env ---
load_dotenv()
BASE = Path(__file__).resolve().parents[1]  # backend/
DOCS_DIR = BASE.parent / "docs" / "cbk_pdfs"
OUT_DIR = BASE / "data" / "faiss_index"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Local model lazy loader ---
_MODEL = None
def get_local_model():
    global _MODEL
    if _MODEL is None:
        print(f"[embed] Loading local model '{EMBED_MODEL_LOCAL}' (sentence-transformers)...")
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(EMBED_MODEL_LOCAL)
        print("[embed] Local model loaded.")
    return _MODEL

# --- OpenAI client (lazy) ---
def get_openai_client():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set (required when USE_LOCAL_EMBEDDINGS=0)")
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)

# --- Helpers ---
def chunk_text(text: str, max_chars: int = 1500, overlap: int = 100) -> list[str]:
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i : i + max_chars]
        chunks.append(chunk)
        i += max_chars - overlap
    return [c.strip() for c in chunks if c.strip()]

def embed_texts(texts: list[str], batch_size: int = 64) -> np.ndarray:
    """
    Embeds texts using either the local SentenceTransformer model (default) or OpenAI
    depending on USE_LOCAL flag / env. Returns float32 np.ndarray (n_texts, dim).
    """
    if USE_LOCAL:
        model = get_local_model()
        vecs = model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True)
        vecs = vecs.astype(np.float32)
        # Normalize for cosine similarity
        faiss.normalize_L2(vecs)
        return vecs
    else:
        client = get_openai_client()
        all_vecs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            resp = client.embeddings.create(model=EMBED_MODEL_OPENAI, input=batch)
            batch_vecs = [d.embedding for d in resp.data]
            all_vecs.extend(batch_vecs)
            print(f"[embed][openai] {i+len(batch)}/{len(texts)} chunks embedded")
        vecs = np.array(all_vecs, dtype=np.float32)
        faiss.normalize_L2(vecs)
        return vecs

# --- Local docs ---
def read_local_docs() -> list[tuple[str, str]]:
    items = []
    if not DOCS_DIR.exists():
        print(f"[warn] docs dir not found: {DOCS_DIR}")
        return items

    for path in DOCS_DIR.rglob("*"):
        text = None
        if path.suffix.lower() == ".pdf":
            try:
                reader = PdfReader(str(path))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                print(f"[warn] Failed to parse PDF {path}: {e}")
        elif path.suffix.lower() == ".txt":
            try:
                text = path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"[warn] Failed to read TXT {path}: {e}")
        if text and text.strip():
            items.append((str(path), text))
    return items

# --- Web fetch with retry ---
def fetch_with_retry(url, retries=3, delay=5):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CBKBot/1.0)"}
    for i in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"[warn] attempt {i+1} failed for {url}: {e}")
            time.sleep(delay)
    return None

def fetch_cbk_pages(urls: list[str]) -> list[tuple[str, str]]:
    texts = []
    for url in urls:
        html = fetch_with_retry(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)
            texts.append((url, text))
    return texts

# --- Build FAISS index ---
def build_index(all_docs: list[tuple[str, str]]):
    all_chunks = []
    meta = []

    for src, text in all_docs:
        for idx, ch in enumerate(chunk_text(text)):
            all_chunks.append(ch)
            meta.append({"source": src, "chunk_id": idx, "len": len(ch)})

    if not all_chunks:
        print("[ingest] No chunks found. Check your docs and URLs.")
        return

    print(f"[ingest] Embedding {len(all_chunks)} chunks (backend={'local' if USE_LOCAL else 'openai'})...")
    vectors = embed_texts(all_chunks)

    # Cosine similarity index (Inner Product on normalized vectors)
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    # Save index and metadata
    faiss.write_index(index, str(OUT_DIR / "index.faiss"))
    np.save(OUT_DIR / "vectors.npy", vectors)

    with open(OUT_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"chunks": all_chunks, "meta": meta}, f, ensure_ascii=False, indent=2)

    with open(OUT_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump({"embed_backend": "local" if USE_LOCAL else "openai", "embed_model": EMBED_MODEL_LOCAL if USE_LOCAL else EMBED_MODEL_OPENAI}, f)

    print(f"[ingest] Saved FAISS index with {len(all_chunks)} chunks to {OUT_DIR}")

# --- Main ---
def main():
    local_docs = read_local_docs()
    print(f"[ingest] Found {len(local_docs)} local docs")

    urls = [
        "https://www.centralbank.go.ke/",
        "https://www.centralbank.go.ke/our-mission/",
        "https://www.centralbank.go.ke/introduction/",
        "https://www.centralbank.go.ke/former-central-bank-governors/",
        "https://www.centralbank.go.ke/banking-development/",
        "https://www.centralbank.go.ke/key-milestones/",
        "https://www.centralbank.go.ke/currency-history/",
        "https://www.centralbank.go.ke/governance/",
        "https://www.centralbank.go.ke/monetary-policy/",
        "https://www.centralbank.go.ke/securities/treasury-bills/",
        "https://www.centralbank.go.ke/securities/treasury-bonds/",
        "https://www.centralbank.go.ke/national-payments-system/",
        "https://www.centralbank.go.ke/contact-us/",
    ]
    web_docs = fetch_cbk_pages(urls)
    print(f"[ingest] Fetched {len(web_docs)} CBK pages")

    all_docs = local_docs + web_docs
    build_index(all_docs)

if __name__ == "__main__":
    main()
