from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.services.rate_limit import bucket

def add_middleware(app: FastAPI):
    @app.middleware("http")
    async def security_and_limits(request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        if not bucket.allow(ip):
            return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded"})

        body = await request.body()
        if len(body) > settings.MAX_BODY_BYTES:
            return JSONResponse(status_code=413, content={"error": "payload_too_large"})

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
