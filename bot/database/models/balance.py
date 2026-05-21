# ruff: noqa: TC003
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class UserBalanceTransactionModel(Base):
    __tablename__ = "user_balance_transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    type: Mapped[str] = mapped_column(String(32))
    balance_before: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    comment: Mapped[str] = mapped_column(Text, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
