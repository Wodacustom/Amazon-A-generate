import hashlib
import math

from app.core.config import settings


class EmbeddingService:
    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for index in range(settings.embedding_dimensions):
            byte = digest[index % len(digest)]
            values.append((byte / 127.5) - 1.0)
        length = math.sqrt(sum(value * value for value in values)) or 1.0
        return [round(value / length, 6) for value in values]
