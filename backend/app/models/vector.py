from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.db.base import Base
from app.models.mixins import TimestampMixin


class VectorDocument(Base, TimestampMixin):
    __tablename__ = "vector_documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    source_id: Mapped[str] = mapped_column(String(80), index=True)
    content: Mapped[str] = mapped_column(Text)
    document_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dimensions))
