from fastapi import APIRouter
import os
from openai import OpenAI

router = APIRouter()

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)

@router.get("/health")
def health():
    """Basic health check plus OpenAI connectivity test."""
    client = get_client()

    # Test embedding
    try:
        emb = client.embeddings.create(
            model="text-embedding-3-small",
            input="health check"
        )
        emb_ok = True
    except Exception as e:
        return {"status": "error", "stage": "embedding", "detail": str(e)}

    # Test chat completion
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello from health check"}]
        )
        chat_ok = True
        sample_reply = resp.choices[0].message.content.strip()
    except Exception as e:
        return {"status": "error", "stage": "chat", "detail": str(e)}

    return {
        "status": "ok",
        "service": "cbk-chatbot",
        "version": "1.0.0",
        "embedding": emb_ok,
        "chat": chat_ok,
        "sample_reply": sample_reply
    }

@router.get("/metrics")
def metrics():
    # You can expand this later with Prometheus counters
    return {"requests": 0, "errors": 0}
