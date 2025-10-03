from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.logging import configure_logging
from app.services.middleware import add_middleware
from app.routers.health import router as health_router
from app.routers.chat import router as chat_router
from app.routers.calculators import router as calc_router


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="CBK Chatbot (RAG)", version="1.0.0")

    # Add your existing middleware
    add_middleware(app)

    # 🔑 Add CORS middleware
    origins = [
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
        "https://cbk-chat.onrender.com",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],   # allow POST, GET, OPTIONS, etc.
        allow_headers=["*"],   # allow X-API-Key and others
    )

    # Routers
    app.include_router(health_router, prefix="/v1")
    app.include_router(chat_router, prefix="/v1")
    app.include_router(calc_router, prefix="/v1")

    return app


app = create_app()
