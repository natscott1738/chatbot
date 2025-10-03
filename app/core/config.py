import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env first
load_dotenv()

@dataclass
class Settings:
    API_KEY: str = os.getenv("API_KEY", "").strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-3.5-turbo").strip()
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "text-embedding-3-small").strip()
    MAX_BODY_BYTES: int = int(os.getenv("MAX_BODY_BYTES", "1048576").strip())
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60").strip())
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "").strip()

settings = Settings()
