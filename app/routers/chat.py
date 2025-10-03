from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from openai import OpenAI
import numpy as np
from app.security import api_key_dependency
from app.core.config import settings
from app.services.orchestrator import answer_with_retrieval

router = APIRouter()

class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    use_rag: bool = True

class ChatMeta(BaseModel):
    tokens: int
    model: str
    latency_ms: int

class ChatResponse(BaseModel):
    reply: str
    meta: ChatMeta

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _=Depends(api_key_dependency)):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    embed_vec = None
    if req.use_rag:
        emb = client.embeddings.create(model=settings.EMBED_MODEL, input=[req.text])
        embed_vec = np.array(emb.data[0].embedding, dtype=np.float32)
    reply, meta = answer_with_retrieval(req.text, embed_vec)
    return ChatResponse(reply=reply, meta=ChatMeta(**meta))
