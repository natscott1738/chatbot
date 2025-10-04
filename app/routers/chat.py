from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import json
from openai import OpenAI

# --- Import scope guard & normalizer ---
from backend.enforce_scope import enforce_scope, normalize

router = APIRouter()

# --- Wide seed fallbacks ---
SEED_FALLBACKS = {
    "default": (
        "The Central Bank of Kenya (CBK) is Kenya’s monetary authority, established in 1966. "
        "It issues and manages the Kenya Shilling, formulates and implements monetary policy, "
        "regulates and supervises banks and microfinance institutions, manages foreign reserves, "
        "and ensures financial stability. CBK also manages government securities, oversees payment "
        "systems like KEPSs/RTGS, and licenses financial institutions."
    ),
    "securities": (
        "Treasury bills (T‑bills) are short‑term government securities with maturities of 91, 182, "
        "and 364 days. They are sold at a discount and redeemed at face value at maturity. "
        "Treasury bonds (T‑bonds) are medium‑ to long‑term securities (2–30 years) that pay "
        "semi‑annual interest (coupon payments) until maturity. CBK conducts weekly auctions for "
        "T‑bills and periodic auctions for bonds. Investors must open a CDS account, submit bids "
        "through competitive or non‑competitive tenders, and settle payments by the value date. "
        "Infrastructure bonds are tax‑exempt and fund development projects, while savings bonds "
        "target retail investors."
    ),
    "payments": (
        "The Kenya Electronic Payment and Settlement System (KEPSS) is CBK’s Real‑Time Gross "
        "Settlement (RTGS) platform for high‑value and time‑critical payments. It ensures final, "
        "irrevocable settlement between banks. CBK also oversees mobile money platforms like "
        "M‑Pesa, Airtel Money, and PesaLink, as well as card payments and clearing houses. "
        "The National Payment System Act provides the legal framework, and CBK issues guidelines "
        "on interoperability, consumer protection, and risk management."
    ),
    "licensing": (
        "To apply for a microfinance licence, an institution must complete the official Licence "
        "Application Form, provide details of shareholding, directors, and senior officers, and "
        "submit Fit and Proper forms for significant shareholders and directors. Applicants must "
        "demonstrate compliance with minimum capital requirements, governance standards, and "
        "prudential guidelines. Supporting documents include audited financial statements, "
        "business plans, and risk management frameworks. Applications are reviewed by CBK’s "
        "Banking Supervision Department under the Microfinance Act."
    ),
    "prudential": (
        "CBK issues Prudential Guidelines to ensure financial stability. These cover capital "
        "adequacy, liquidity management, corporate governance, risk management, credit "
        "classification, provisioning, and disclosure requirements. Institutions must comply "
        "with Anti‑Money Laundering (AML) and Counter‑Terrorism Financing (CTF) laws, report "
        "to the Financial Reporting Centre (FRC), and share credit information with Credit "
        "Reference Bureaus (CRBs). CBK conducts onsite and offsite inspections to enforce compliance."
    ),
    "currency": (
        "CBK is the sole issuer of the Kenya Shilling (KES). Banknotes are issued in denominations "
        "of 50, 100, 200, 500, and 1000 shillings, while coins include 1, 5, 10, 20, and 40 shillings. "
        "Commemorative coins are occasionally issued to mark national milestones. CBK manages "
        "currency distribution through its branches and currency centres, and educates the public "
        "on security features to combat counterfeiting."
    ),
    "investor": (
        "Investors in government securities must open a Central Depository System (CDS) account "
        "with CBK or through a commercial bank. Required documents include a national ID or passport, "
        "KRA PIN, and passport photo. Investors can participate in T‑bill and T‑bond auctions, "
        "receive semi‑annual coupon payments, and trade securities in the secondary market via the NSE. "
        "CBK also provides investor education, circulars, and auction prospectuses."
    ),
    "legal": (
        "CBK operates under the Central Bank of Kenya Act, the Banking Act, the Microfinance Act, "
        "and the National Payment System Act. It collaborates with the National Treasury, Capital "
        "Markets Authority (CMA), Insurance Regulatory Authority (IRA), Sacco Societies Regulatory "
        "Authority (SASRA), and the Financial Reporting Centre (FRC). These institutions collectively "
        "ensure financial stability, consumer protection, and regulatory compliance."
    )
}

# --- Domain keyword mapping with synonyms ---
DOMAIN_KEYWORDS = {
    "securities": {
        "treasury", "t-bill", "tbill", "t bill", "t bills", "bond", "bonds",
        "auction", "government securities", "cds", "coupon", "yield", "maturity"
    },
    "payments": {
        "keps", "kepss", "rtgs", "payment", "settlement", "mobile money",
        "pesalink", "mpesa", "airtel money", "switch", "clearing house"
    },
    "licensing": {
        "licence", "license", "microfinance", "fit and proper", "application form",
        "shareholding", "directors", "senior officers", "capital adequacy"
    },
    "prudential": {
        "prudential", "capital adequacy", "liquidity", "risk management",
        "supervision", "npl", "non-performing", "credit classification"
    },
    "currency": {
        "currency", "shilling", "kes", "banknote", "coin", "coins",
        "commemorative", "legal tender", "denomination"
    },
    "investor": {
        "investor", "cds account", "coupon", "prospectus", "secondary market",
        "auction prospectus", "rollover", "portfolio"
    },
    "legal": {
        "act", "regulation", "law", "treasury", "cma", "ira", "sasra", "frc",
        "banking act", "microfinance act", "cbk act", "national payment system act"
    }
}

# --- Pick fallback based on query ---
def pick_fallback(query: str) -> str:
    q = normalize(query)
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                return SEED_FALLBACKS[domain]
    return SEED_FALLBACKS["default"]

# --- Retrieval stub (replace with FAISS/Qdrant search) ---
def retrieve_cbk_docs(query: str, top_k: int = 3):
    try:
        with open("backend/data/faiss_index/meta.json", encoding="utf-8") as f:
            meta = json.load(f)
        chunks = meta["chunks"]
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
        model="gpt-4o-mini",
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
        return result
    scope_response, seed_fallback = result

    # 2. Retrieve docs
    docs = retrieve_cbk_docs(query, top_k=3)

    # 3. If retrieval fails, use topic-specific fallback
    if not docs:
        return {"reply": pick_fallback(query)}

    # 4. Build prompt
    context = "\n\n".join(docs)
    system_instruction = (
        "You are CBK Assistant. Only answer using the provided CBK documents. "
        "If the answer is not in them, fall back to the seed knowledge."
    )
    prompt = f"{system_instruction}\n\nContext:\n{context}\n\nUser: {query}\nAssistant:"

    # 5. Call model
    reply = call_model(prompt)

    # 6. Post-check: if model drifts, use topic-specific fallback
    if "Central Bank" not in reply and "CBK" not in reply:
        return {"reply": pick_fallback(query)}

    return {"reply": reply}
