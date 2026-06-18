from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(50), default="queued", index=True)
    progress: Mapped[int] = mapped_column(default=0)
    current_step: Mapped[str | None] = mapped_column(String(100))
    input_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text)


class AgentResult(Base, TimestampMixin):
    __tablename__ = "agent_results"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"))
    content_modules: Mapped[list[dict]] = mapped_column(JSON, default=list)
    image_prompts: Mapped[list[dict]] = mapped_column(JSON, default=list)
    model_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
