import re
from fastapi.responses import JSONResponse

# --- Chit-chat whitelist ---
CHITCHAT = {
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "thanks", "thank you", "thx", "ok", "okay", "cool", "welcome"
}

# --- Expanded CBK keyword set ---
CBK_KEYWORDS = [
    # Core identifiers
    "central bank", "central bank of kenya", "cbk", "banki kuu", "monetary authority",
    "cbk kenya", "cbk governor", "board of cbk", "monetary policy committee", "mpc",

    # Currency & monetary policy
    "kenya shilling", "kes", "currency", "exchange rate", "forex", "fx", "inflation",
    "interest rate", "monetary policy", "policy rate", "cbk rate", "cbr",
    "foreign reserves", "balance of payments", "money supply", "liquidity",
    "inflation target", "price stability",

    # Government securities
    "treasury bill", "t-bill", "treasury bond", "government securities", "bond auction",
    "repo", "reverse repo", "open market operations", "omo", "liquidity management",
    "auction results", "cut-off rate", "weighted average rate", "yield curve",
    "bond prospectus", "infrastructure bond", "savings bond", "coupon rate",
    "discount rate", "rediscount", "secondary market", "nairobi securities exchange",
    "application form", "tender box", "value date", "maturity date", "rollover",
    "withholding tax", "tax exemption", "virtual account", "cds account",
    "portfolio account number", "nominee account", "diaspora investment",

    # Licensing & regulatory
    "licence application", "licensing", "deposit taking", "microfinance", "microfinance bank",
    "community microfinance", "nationwide microfinance", "fit and proper", "significant shareholder",
    "shareholding", "directorship", "professional suitability", "reputational suitability",
    "employment record", "sources of funds", "borrowings", "declaration", "commissioner for oaths",
    "magistrate", "witnessed before me", "identification card", "passport number",
    "pin number", "postal address", "physical address", "educational qualifications",
    "professional qualifications", "bankers", "referees", "confidential information",

    # Prudential guidelines & supervision
    "prudential guidelines", "banking supervision", "capital adequacy", "liquidity ratio",
    "risk management", "internal controls", "ifrs", "tax implications", "product approval",
    "market research", "competences", "new product", "conversion", "non-bank financial institution",
    "nbfi", "commercial bank", "approval date", "credit reference bureau", "crb",
    "non-performing loans", "npl", "financial stability report", "annual report", "supervision report",

    # Payment systems
    "payment system", "kepss", "rtgs", "real time gross settlement",
    "kenya electronic payment and settlement system", "mobile money",
    "mpesa", "airtel money", "pesalink", "national payment system",
    "switch operator", "settlement account", "clearing house", "intraday liquidity facility",
    "repo facility", "repurchase agreement",

    # Customer-facing services
    "commemorative coin", "kenya@50", "cbk@50", "gold coin", "silver coin", "nickel brass coin",
    "coin sale", "request form", "amount payable", "organization", "payment mode",
    "internet banking", "ib registration", "business internet banking", "foreign exchange services",
    "omo securities", "government securities portal", "approver", "inputter", "mandate number",
    "authorized signatory", "sms groups", "official email", "mobile number",

    # Legal & institutional
    "cbk act", "banking act", "microfinance act", "national payment system act",
    "prudential regulations", "anti-money laundering", "aml", "proceeds of crime act",
    "financial reporting centre", "frc", "capital markets authority", "cma",
    "insurance regulatory authority", "ira", "sacco societies regulatory authority", "sasra",
    "national treasury", "ministry of finance", "governor statement", "press release", "circular", "guideline"
]

# --- Normalization ---
def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()

# --- Scope check ---
def is_cbk_related(query: str) -> bool:
    q = normalize(query)
    if q in CHITCHAT:
        return True
    if any(k in q for k in CBK_KEYWORDS):
        return True
    tokens = q.split()
    important = {"cbk", "central", "bank", "kenya", "shilling", "treasury", "bond"}
    if any(tok in important for tok in tokens):
        return True
    return False

# --- Enforce scope with fallbacks ---
def enforce_scope(query: str):
    q = normalize(query)

    # Handle chit-chat
    if q in {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}:
        return JSONResponse({"reply": "Hello! I can help you with information about the Central Bank of Kenya."}, status_code=200)
    if q in {"thanks", "thank you", "thx"}:
        return JSONResponse({"reply": "You’re welcome! Happy to help with CBK‑related questions anytime."}, status_code=200)

    # Out-of-scope
    if not is_cbk_related(query):
        return JSONResponse(
            {"reply": "I can only answer questions related to the Central Bank of Kenya and its policies."},
            status_code=200
        )

    # In-scope but retrieval may fail → provide seed fallback
    seed_fallback = (
        "The Central Bank of Kenya (CBK) is Kenya’s monetary authority, established in 1966. "
        "It issues and manages the Kenya Shilling, formulates and implements monetary policy, "
        "regulates and supervises banks and microfinance institutions, manages foreign reserves, "
        "and ensures financial stability. CBK also manages government securities such as Treasury bills "
        "and bonds, oversees payment systems like KEPSs/RTGS, and licenses financial institutions. "
        "For licensing (e.g. microfinance), applicants must complete official forms, submit Fit and Proper "
        "declarations, meet capital adequacy requirements, and provide supporting documents under the "
        "Microfinance Act and CBK regulations."
    )

    return None, seed_fallback
