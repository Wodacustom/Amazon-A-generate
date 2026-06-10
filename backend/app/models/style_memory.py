from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class StyleMemory(Base, TimestampMixin):
    __tablename__ = "style_memories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_type: Mapped[str] = mapped_column(String(20), index=True)
    owner_id: Mapped[UUID] = mapped_column(index=True)
    style_name: Mapped[str] = mapped_column(String(255))
    style_summary: Mapped[str | None] = mapped_column(Text)
    visual_keywords: Mapped[dict] = mapped_column(JSON, default=list)
    color_palette: Mapped[dict] = mapped_column(JSON, default=list)
    layout_preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    copywriting_tone: Mapped[dict] = mapped_column(JSON, default=dict)
    negative_preferences: Mapped[dict] = mapped_column(JSON, default=list)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StyleMemoryEvent(Base):
    __tablename__ = "style_memory_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    style_memory_id: Mapped[UUID] = mapped_column(ForeignKey("style_memories.id", ondelete="CASCADE"), index=True)
    source_result_id: Mapped[UUID | None] = mapped_column(ForeignKey("generation_results.id"))
    user_feedback: Mapped[str | None] = mapped_column(Text)
    extracted_style_delta: Mapped[dict] = mapped_column(JSON, default=dict)
    update_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
