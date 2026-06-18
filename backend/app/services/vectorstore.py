from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vector import VectorDocument
from app.services.embedding import EmbeddingService


class VectorStore:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
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
        embedding = self.embedding_service.embed(query)
        statement = select(VectorDocument).order_by(VectorDocument.embedding.cosine_distance(embedding)).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars())
