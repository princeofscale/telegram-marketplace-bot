# ruff: noqa: TC003
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class DepositModel(Base):
    __tablename__ = "deposits"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    requested_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default="0")
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default="0")
    payment_method: Mapped[str] = mapped_column(String(64))
    provider_payment_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    payment_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
