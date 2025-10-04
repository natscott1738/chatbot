from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
from openai import OpenAI
import numpy as np
import json
import re


# --- Router setup ---
router = APIRouter()

# --- Scope guard utility ---
# Expanded keyword set
CBK_KEYWORDS = [
    # Core identifiers
    "central bank", "central bank of kenya", "cbk", "banki kuu", "monetary authority",
    "cbk kenya", "cbk governor", "board of cbk", "monetary policy committee", "mpc",

    # Currency & monetary policy
    "kenya shilling", "kes", "currency", "exchange rate", "forex", "fx", "inflation",
    "interest rate", "monetary policy", "policy rate", "cbk rate", "cbr",
    "foreign reserves", "balance of payments", "money supply", "liquidity",
    "inflation target", "price stability",

    # Government securities (from securities_faqs, treasury_bills_bonds_application_form)
    "treasury bill", "t-bill", "treasury bond", "government securities", "bond auction",
    "repo", "reverse repo", "open market operations", "omo", "liquidity management",
    "auction results", "cut-off rate", "weighted average rate", "yield curve",
    "bond prospectus", "infrastructure bond", "savings bond", "coupon rate",
    "discount rate", "rediscount", "secondary market", "nairobi securities exchange",
    "application form", "tender box", "value date", "maturity date", "rollover",
    "withholding tax", "tax exemption", "virtual account", "cds account",
    "portfolio account number", "nominee account", "diaspora investment",

    # Licensing & regulatory forms (from LicenceApplicationFormMicrofinanceBank,
    # FitProperFormDirectorsSeniorOfficersMicrofinanceBanks, FitProperFormSignificantShareholdersMicrofinanceBanks,
    # NotesCompletionApplicationFormsMicrofinanceBanks)
    "licence application", "licensing", "deposit taking", "microfinance", "microfinance bank",
    "community microfinance", "nationwide microfinance", "fit and proper", "significant shareholder",
    "shareholding", "directorship", "professional suitability", "reputational suitability",
    "employment record", "sources of funds", "borrowings", "declaration", "commissioner for oaths",
    "magistrate", "witnessed before me", "personal information", "identification card", "passport number",
    "pin number", "postal address", "physical address", "educational qualifications", "professional qualifications",
    "bankers", "referees", "confidential information", "privacy statement", "customer agreement",
    "terms and conditions", "national treasury", "county government", "government agency",

    # Supervision & prudential guidelines (from DTMs-New-Products-Guidelines, Conversions)
    "prudential guidelines", "banking supervision", "capital adequacy", "liquidity ratio",
    "risk management", "internal controls", "ifrs", "tax implications", "withholding tax",
    "product approval", "market research", "competences", "new product", "deposit taking microfinance",
    "conversion", "non-bank financial institution", "nbfi", "commercial bank", "approval date",

    # CBK services & forms (from Commemorative-Coins-Request-Form, CommercialBanksIBRegistration)
    "commemorative coin", "kenya@50", "cbk@50", "gold coin", "silver coin", "nickel brass coin",
    "coin sale", "request form", "amount payable", "organization", "payment mode",
    "internet banking", "ib registration", "business internet banking", "foreign exchange services",
    "omo securities", "government securities", "approver", "inputter", "mandate number",
    "authorized signatory", "sms groups", "official email", "mobile number", "confidential information",
    "privacy statement", "customer agreement", "acceptance of terms",

    # Payment systems
    "payment system", "kepss", "rtgs", "real time gross settlement",
    "kenya electronic payment and settlement system", "mobile money",
    "mpesa", "airtel money", "pesalink", "national payment system",
    "switch operator", "settlement account", "clearing house", "intraday liquidity facility",
    "repo facility", "repurchase agreement",

    # Institutional & legal references
    "cbk act", "banking act", "microfinance act", "prudential regulations",
    "anti-money laundering", "aml", "proceeds of crime act",
    "financial reporting centre", "frc", "capital markets authority", "cma",
    "insurance regulatory authority", "ira", "sacco societies regulatory authority", "sasra",
    "national treasury", "ministry of finance", "financial stability report", "annual report",
    "press release", "circular", "guideline", "supervision report", "governor statement"
]

def normalize(text: str) -> str:
    """Lowercase and strip punctuation for easier matching."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())

def is_cbk_related(query: str) -> bool:
    q = normalize(query)
    # Direct keyword match
    if any(k in q for k in CBK_KEYWORDS):
        return True
    # Fuzzy: allow partial matches on important tokens
    tokens = q.split()
    important = {"cbk", "central", "bank", "kenya", "shilling", "treasury", "bond"}
    if any(tok in important for tok in tokens):
        return True
    return False

def enforce_scope(query: str):
    """
    Returns None if query is in scope.
    Returns a JSONResponse refusal if query is out of scope.
    """
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
