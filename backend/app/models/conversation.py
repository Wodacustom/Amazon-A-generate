from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ConversationSession(Base, TimestampMixin):
    __tablename__ = "conversation_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id"))
    task_id: Mapped[UUID | None] = mapped_column(ForeignKey("generation_tasks.id"))
    current_result_id: Mapped[UUID | None] = mapped_column(ForeignKey("generation_results.id"))
    status: Mapped[str] = mapped_column(String(50), default="active")
    context: Mapped[dict] = mapped_column(JSON, default=dict)


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(String(50), default="text")
    related_image_version_id: Mapped[UUID | None] = mapped_column()
    message_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ImageVersion(Base):
    __tablename__ = "image_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("products.id"))
    parent_image_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("image_versions.id"))
    image_url: Mapped[str] = mapped_column(Text)
    storage_key: Mapped[str | None] = mapped_column(Text)
    prompt: Mapped[str | None] = mapped_column(Text)
    edit_instruction: Mapped[str | None] = mapped_column(Text)
    version_no: Mapped[int] = mapped_column(Integer)
    image_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
