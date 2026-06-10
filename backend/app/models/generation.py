from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class GenerationTask(Base, TimestampMixin):
    __tablename__ = "generation_tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str | None] = mapped_column(String(100))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text)


class GenerationResult(Base):
    __tablename__ = "generation_results"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("generation_tasks.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id"))
    modules: Mapped[list[dict]] = mapped_column(JSON, default=list)
    preview_url: Mapped[str | None] = mapped_column(Text)
    export_urls: Mapped[dict] = mapped_column(JSON, default=dict)
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
