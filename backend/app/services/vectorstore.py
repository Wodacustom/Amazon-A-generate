"""pgvector 检索服务。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.vector import VectorDocument
from app.services.embedding import EmbeddingService

logger = get_logger(__name__)


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
        embedding = await self.embedding_service.embed(content, db)
        document = VectorDocument(
            source_type=source_type,
            source_id=source_id,
            content=content,
            document_metadata=metadata or {},
            embedding=embedding,
        )
        db.add(document)
        await db.flush()
        logger.info(
            "vector.document.added",
            extra={
                "event": "vector.document.added",
                "document_id": str(document.id),
                "source_type": source_type,
                "source_id": source_id,
                "content_length": len(content),
                "metadata_keys": list((metadata or {}).keys()),
            },
        )
        return document

    async def search(self, db: AsyncSession, query: str, limit: int = 5) -> list[VectorDocument]:
        """按余弦距离检索最相近的文档。"""
        embedding = await self.embedding_service.embed(query, db)
        statement = select(VectorDocument).order_by(VectorDocument.embedding.cosine_distance(embedding)).limit(limit)
        result = await db.execute(statement)
        documents = list(result.scalars())
        logger.info(
            "vector.search.finish",
            extra={
                "event": "vector.search.finish",
                "query_length": len(query),
                "limit": limit,
                "result_count": len(documents),
            },
        )
        return documents
