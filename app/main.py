from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(title="CBK Chatbot (RAG)", version="1.0.0")
    return app

app = create_app()

@app.get("/health")
def health():
    return {"status": "ok"}
