"""pgvector 检索服务。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vector import VectorDocument
from app.services.embedding import EmbeddingService


class VectorStore:
    """封装向量文档写入和相似度检索。"""

    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        """允许注入 embedding 服务，便于测试或替换真实模型。"""
        self.embedding_service = embedding_service or EmbeddingService()

    async def add_document(
        self,
        db: AsyncSession,
        *,
        source_type: str,
        source_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> VectorDocument:
        """写入一条可检索文档。"""
        document = VectorDocument(
            source_type=source_type,
            source_id=source_id,
            content=content,
            document_metadata=metadata or {},
            embedding=self.embedding_service.embed(content),
        )
        db.add(document)
        await db.flush()
        return document

    async def search(self, db: AsyncSession, query: str, limit: int = 5) -> list[VectorDocument]:
        """按余弦距离检索最相近的文档。"""
        embedding = self.embedding_service.embed(query)
        statement = select(VectorDocument).order_by(VectorDocument.embedding.cosine_distance(embedding)).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars())
