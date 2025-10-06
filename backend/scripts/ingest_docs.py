import os
import json
import faiss
import time
import numpy as np
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv

# --- Load env ---
load_dotenv()
BASE = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE.parent / "docs" / "cbk_pdfs"
OUT_DIR = BASE / "data" / "faiss_index"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- OpenAI client ---
def get_client():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
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

def embed_texts(client: OpenAI, texts: list[str], batch_size: int = 50) -> np.ndarray:
    """Batch embeddings to reduce API calls."""
    all_vecs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
        vecs = [d.embedding for d in resp.data]
        all_vecs.extend(vecs)
        print(f"[embed] {i+len(batch)}/{len(texts)} chunks embedded")
    return np.array(all_vecs, dtype=np.float32)

# --- Local docs ---
def read_local_docs() -> list[tuple[str, str]]:
    items = []
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
    client = get_client()
    all_chunks, meta = [], {"chunks": []}

    for src, text in all_docs:
        for idx, ch in enumerate(chunk_text(text)):
            all_chunks.append(ch)
            meta["chunks"].append({"source": src, "chunk_id": idx, "len": len(ch)})

    if not all_chunks:
        print("[ingest] No chunks found. Check your docs and URLs.")
        return

    print(f"[ingest] Embedding {len(all_chunks)} chunks...")
    vectors = embed_texts(client, all_chunks)

    # Build FAISS index
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save
    faiss.write_index(index, str(OUT_DIR / "index.faiss"))
    with open(OUT_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"chunks": all_chunks, "meta": meta["chunks"]}, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump({"embed_model": EMBED_MODEL}, f)

    print(f"[ingest] Saved FAISS index with {len(all_chunks)} chunks to {OUT_DIR}")

# --- Main ---
def main():
    # Local docs
    local_docs = read_local_docs()
    print(f"[ingest] Found {len(local_docs)} local docs")

    # CBK URLs (expand as needed)
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
        "https://www.centralbank.go.ke/national-payment-system/"
        "https://www.centralbank.go.ke/contact-us/",
    ]
    web_docs = fetch_cbk_pages(urls)
    print(f"[ingest] Fetched {len(web_docs)} CBK pages")

    all_docs = local_docs + web_docs
    build_index(all_docs)

if __name__ == "__main__":
    main()
