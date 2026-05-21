# ruff: noqa: TC003
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    product_id: Mapped[UUID] = mapped_column(index=True)
    inventory_item_id: Mapped[UUID] = mapped_column(index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    buy_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    sell_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    profit: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(32), index=True)
    delivered_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
