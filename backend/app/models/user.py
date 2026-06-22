"""系统用户表。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemUser(Base):
    """系统用户。"""

    __tablename__ = "system_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(32))
    avatar: Mapped[str | None] = mapped_column(String(128))
    create_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    deleted: Mapped[int] = mapped_column(SmallInteger, default=0)
