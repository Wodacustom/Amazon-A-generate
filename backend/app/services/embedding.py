"""MVP 阶段的 mock embedding 服务。"""

import hashlib
import math

from app.core.config import settings


class EmbeddingService:
    """生成固定维度、可重复的伪向量。"""

    def embed(self, text: str) -> list[float]:
        """用 SHA-256 将文本稳定映射到配置维度。"""
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for index in range(settings.embedding_dimensions):
            byte = digest[index % len(digest)]
            values.append((byte / 127.5) - 1.0)
        # 归一化后便于用 cosine distance 做相似度排序。
        length = math.sqrt(sum(value * value for value in values)) or 1.0
        return [round(value / length, 6) for value in values]
