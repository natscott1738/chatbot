from fastapi import Header, HTTPException
from app.core.config import settings

def api_key_dependency(x_api_key: str = Header(..., alias="X-API-Key")):
    if not settings.API_KEY or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
