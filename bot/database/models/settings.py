from __future__ import annotations
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class SettingModel(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[dict[str, Any] | bool | str | int | float] = mapped_column(JSON)
    description: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.utcnow,
    )
