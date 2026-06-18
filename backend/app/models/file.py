from uuid import UUID, uuid4

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class FileAsset(Base, TimestampMixin):
    __tablename__ = "files"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    object_key: Mapped[str] = mapped_column(Text, unique=True, index=True)
    bucket: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[str | None] = mapped_column(String(255))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    url: Mapped[str] = mapped_column(Text)
