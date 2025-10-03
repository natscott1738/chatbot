import time
from typing import Optional, Tuple
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a concise assistant for CBK-related FAQs. "
    "Ground answers in retrieved context when provided. "
    "Do not perform financial calculations—defer to calculators. "
    "Keep responses clear, safe, and under 120 words unless asked."
)

def chat_reply(text: str, context: Optional[str]) -> Tuple[str, dict]:
    start = time.time()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "system", "content": f"Context:\n{context}"})
    messages.append({"role": "user", "content": text})

    resp = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=256,
        timeout=10,
    )
    choice = resp.choices[0].message.content.strip()
    tokens = getattr(resp, "usage", None).total_tokens if getattr(resp, "usage", None) else 0
    latency_ms = int((time.time() - start) * 1000)
    return choice, {"tokens": tokens, "model": settings.CHAT_MODEL, "latency_ms": latency_ms}
