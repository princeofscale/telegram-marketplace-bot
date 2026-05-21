from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import BigInteger, DateTime, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base, big_int_pk, created_at


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[big_int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    language_code: Mapped[str | None]
    referrer: Mapped[str | None]
    created_at: Mapped[created_at]

    role: Mapped[str] = mapped_column(String(16), default=UserRole.USER.value, server_default=UserRole.USER.value)
    invited_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    referrals_count: Mapped[int] = mapped_column(default=0, server_default="0")
    referral_earnings: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default="0")
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default="0")
    total_deposited: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default="0")
    total_spent: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), server_default="0")
    banned_reason: Mapped[str | None] = mapped_column(nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.utcnow,
    )

    is_admin: Mapped[bool] = mapped_column(default=False)
    is_suspicious: Mapped[bool] = mapped_column(default=False)
    is_block: Mapped[bool] = mapped_column(default=False)
    is_blocked: Mapped[bool] = mapped_column(default=False, server_default="false")
    is_premium: Mapped[bool] = mapped_column(default=False)
