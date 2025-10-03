from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "service": "cbk-chatbot", "version": "1.0.0"}

@router.get("/metrics")
def metrics():
    return {"requests": 0, "errors": 0}
