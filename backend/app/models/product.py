"""产品数据表。"""

from uuid import UUID, uuid4

from sqlalchemy import JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Product(Base, TimestampMixin):
    """MVP 阶段的产品草稿。"""

    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(String(50), default="amazon")
    country: Mapped[str] = mapped_column(String(50), default="US")
    language: Mapped[str] = mapped_column(String(50), default="zh-CN")
    selling_points: Mapped[list[str]] = mapped_column(JSON, default=list)
    specs: Mapped[dict] = mapped_column(JSON, default=dict)
    description: Mapped[str | None] = mapped_column(Text)
    file_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
