"""模型配置、路由和模板表。"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelProfile(Base):
    """可调用模型档案。"""

    __tablename__ = "model_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    model_type: Mapped[str] = mapped_column(String(32))
    provider: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(128))
    base_url: Mapped[str | None] = mapped_column(String(512))
    encrypted_api_key: Mapped[str | None] = mapped_column(Text)
    timeout_seconds: Mapped[float] = mapped_column(Float, default=60.0)
    temperature: Mapped[float | None] = mapped_column(Float)
    dimensions: Mapped[int | None] = mapped_column(Integer)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    create_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(Integer, default=0)


class ModelRoute(Base):
    """业务角色到模型档案的路由。"""

    __tablename__ = "model_routes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(80), unique=True)
    primary_profile_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("model_profiles.id"))
    fallback_profile_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("model_profiles.id"))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    create_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(Integer, default=0)


class ModelRequestTemplate(Base):
    """模型请求模板。"""

    __tablename__ = "model_request_templates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(120))
    version: Mapped[str] = mapped_column(String(40), default="v1")
    system_prompt: Mapped[str] = mapped_column(Text)
    user_template: Mapped[str] = mapped_column(Text)
    response_contract: Mapped[str] = mapped_column(String(120))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    create_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(Integer, default=0)


class ModelConfigAuditLog(Base):
    """模型配置审计日志。"""

    __tablename__ = "model_config_audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(80))
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[str | None] = mapped_column(String(80))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    create_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
