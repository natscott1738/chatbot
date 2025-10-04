import os
import json
import numpy as np
from pathlib import Path
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE.parent / "docs" / "cbk_pdfs"   # recursive walk
OUT_DIR = BASE / "data" / "faiss_index"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def read_pdfs() -> list[dict]:
    items = []
    for pdf_path in DOCS_DIR.rglob("*.pdf"):   # recursive glob
        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        category = pdf_path.parent.name
        items.append({
            "source": pdf_path.name,
            "category": category,
            "text": text
        })
    return items

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 100) -> list[str]:
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i : i + max_chars]
        chunks.append(chunk)
        i += max_chars - overlap
    return [c.strip() for c in chunks if c.strip()]

def embed_texts(client: OpenAI, texts: list[str]) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = [d.embedding for d in resp.data]
    return np.array(vecs, dtype=np.float32)

def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    client = OpenAI(api_key=OPENAI_API_KEY)

    items = read_pdfs()
    print(f"[ingest] Found {len(items)} PDFs")

    all_chunks, meta = [], []
    for item in items:
        chunks = chunk_text(item["text"])
        for idx, ch in enumerate(chunks):
            meta.append({
                "source": item["source"],
                "category": item["category"],
                "chunk_id": idx,
                "len": len(ch)
            })
        all_chunks.extend(chunks)

    print(f"[ingest] Chunked into {len(all_chunks)} segments")

    if not all_chunks:
        print("[ingest] No chunks to embed. Check DOCS_DIR path and files.")
        return

    vectors = embed_texts(client, all_chunks)
    print(f"[ingest] Embedded into shape {vectors.shape}")

    np.save(OUT_DIR / "vectors.npy", vectors)
    with open(OUT_DIR / "meta.json", "w") as f:
        json.dump({"chunks": all_chunks, "meta": meta}, f)
    with open(OUT_DIR / "config.json", "w") as f:
        json.dump({"embed_model": EMBED_MODEL}, f)

    print("[ingest] Saved index:", OUT_DIR)

if __name__ == "__main__":
    main()
