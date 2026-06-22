"""Embedding 服务门面。"""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.models import ModelService


class EmbeddingService:
    """通过统一模型网关生成向量。"""

    def __init__(self, model_service: ModelService | None = None) -> None:
        self.model_service = model_service or ModelService()

    async def embed(self, text: str, db: AsyncSession | None = None) -> list[float]:
        """生成单条文本向量。"""
        return await self.model_service.embed_query(text, db=db, role="retrieval_embedding")

    async def embed_documents(self, texts: Sequence[str], db: AsyncSession | None = None) -> list[list[float]]:
        """批量生成文档向量。"""
        return await self.model_service.embed_documents(texts, db=db, role="retrieval_embedding")
