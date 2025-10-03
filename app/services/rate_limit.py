import time
from typing import Dict
from app.core.config import settings

class TokenBucket:
    def __init__(self, rate_per_minute: int):
        self.rate = rate_per_minute
        self.buckets: Dict[str, dict] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        b = self.buckets.get(key)
        if not b:
            self.buckets[key] = {"tokens": self.rate, "updated": now}
            return True
        elapsed = now - b["updated"]
        refill = int(elapsed / 60 * self.rate)
        if refill > 0:
            b["tokens"] = min(self.rate, b["tokens"] + refill)
            b["updated"] = now
        if b["tokens"] > 0:
            b["tokens"] -= 1
            return True
        return False

bucket = TokenBucket(rate_per_minute=settings.RATE_LIMIT_PER_MINUTE)
