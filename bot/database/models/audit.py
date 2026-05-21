# ruff: noqa: TC003
from __future__ import annotations
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, BigInteger, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    actor_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
