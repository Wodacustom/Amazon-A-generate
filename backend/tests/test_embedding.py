"""mock embedding 服务测试。"""

import asyncio

from app.core.config import settings
from app.services.embedding import EmbeddingService


def test_mock_embedding_is_deterministic_and_configured_dimension():
    """验证同一文本生成稳定向量，且维度来自配置。"""
    service = EmbeddingService()

    first = asyncio.run(service.embed("portable grinder"))
    second = asyncio.run(service.embed("portable grinder"))

    assert first == second
    assert len(first) == settings.embedding_dimensions
