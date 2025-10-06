import re
import os
import numpy as np
from fastapi.responses import JSONResponse
from openai import OpenAI

# --- Normalization ---
def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()

# --- Seed scope phrases ---
SCOPE_SEEDS = [
    "central bank of kenya",
    "cbk",
    "kenya shilling",
    "treasury bills",
    "treasury bonds",
    "government securities",
    "cds account",
    "cbk governor",
    "monetary policy",
    "prudential guidelines",
    "microfinance licensing",
    "payment systems",
    "kepss",
    "rtgs",
    "cbk act",
    "financial stability",
]

# --- Definition-first snippets ---
SAFE_SNIPPETS = {
    "governor": (
        "The CBK Governor is the chief executive officer of the Central Bank of Kenya. "
        "The current Governor is Dr. Kamau Thugge, in office since June 19, 2023."
    ),
    "cds_account": (
        "A Central Depository System (CDS) account is required to invest in Government securities "
        "like Treasury bills and bonds. It records your holdings, enables transfers, and is opened "
        "through the Central Bank of Kenya or an authorized agent."
    ),
    "board": (
        "The CBK Board of Directors provides oversight of the Bank’s management, approves policies, "
        "and ensures accountability in line with the CBK Act."
    ),
    "mpc": (
        "The Monetary Policy Committee (MPC) formulates monetary policy, sets the Central Bank Rate (CBR), "
        "and guides actions to maintain price stability and support economic growth."
    ),
    "t_bills_vs_bonds": (
        "Treasury bills are short-term securities (91, 182, or 364 days) sold at a discount. "
        "Treasury bonds are longer-term (1–30 years) and pay semi-annual interest. "
        "Both are issued by CBK on behalf of the Government of Kenya."
    ),
}

GENERIC_FALLBACK = (
    "The Central Bank of Kenya (CBK) is Kenya’s monetary authority, established in 1966. "
    "It issues and manages the Kenya Shilling, formulates and implements monetary policy, "
    "regulates and supervises banks and microfinance institutions, manages foreign reserves, "
    "and ensures financial stability. CBK also manages government securities, oversees payment "
    "systems like KEPSs/RTGS, and licenses financial institutions."
)

# --- Lazy embedding cache ---
SEED_EMBEDS = None

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)

def embed_text(text: str):
    client = get_client()
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(resp.data[0].embedding, dtype="float32")

def get_seed_embeds():
    global SEED_EMBEDS
    if SEED_EMBEDS is None:
        print("[info] Computing seed embeddings for scope guard...")
        SEED_EMBEDS = [embed_text(seed) for seed in SCOPE_SEEDS]
    return SEED_EMBEDS

# --- Similarity helper ---
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def is_cbk_related(query: str, threshold: float = 0.65) -> bool:
    q_embed = embed_text(query)
    sims = [cosine_sim(q_embed, s) for s in get_seed_embeds()]
    return max(sims) >= threshold

# --- Intent detection ---
def detect_intent(query: str):
    q = query.lower()
    if "governor" in q:
        return "governor"
    if "cds" in q and "account" in q:
        return "cds_account"
    if "board" in q and "director" in q:
        return "board"
    if "monetary policy committee" in q or "mpc" in q:
        return "mpc"
    if "treasury bill" in q and "bond" in q:
        return "t_bills_vs_bonds"
    return None

# --- Enforce scope ---
def enforce_scope(query: str):
    q = normalize(query)

    # Handle chit-chat quickly
    if q in {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}:
        return JSONResponse({"reply": "Hello! I can help you with information about the Central Bank of Kenya."}, status_code=200)
    if q in {"thanks", "thank you", "thx"}:
        return JSONResponse({"reply": "You’re welcome! Happy to help with CBK‑related questions anytime."}, status_code=200)

    # 🔑 Intent detection FIRST
    intent = detect_intent(query)
    if intent and intent in SAFE_SNIPPETS:
        return JSONResponse({"reply": SAFE_SNIPPETS[intent]}, status_code=200)

    # Out-of-scope check SECOND
    try:
        if not is_cbk_related(query, threshold=0.65):  # relaxed threshold
            return JSONResponse(
                {"reply": "I can only answer questions related to the Central Bank of Kenya and its policies."},
                status_code=200
            )
    except Exception as e:
        print(f"[error] Scope check failed: {e}")
        return JSONResponse(
            {"reply": "Internal error while checking scope. Please try again later."},
            status_code=500
        )

    # In-scope but no specific intent → let chat.py handle retrieval
    return None, GENERIC_FALLBACK
