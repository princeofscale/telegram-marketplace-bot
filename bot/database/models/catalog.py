# ruff: noqa: TC003
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base


class SourceProductModel(Base):
    __tablename__ = "source_products"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source: Mapped[str] = mapped_column(String(64), index=True)
    source_item_id: Mapped[str] = mapped_column(String(128), index=True)
    raw_title: Mapped[str] = mapped_column(String(512))
    raw_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.utcnow,
    )


class CatalogProductModel(Base):
    __tablename__ = "catalog_products"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_product_id: Mapped[UUID | None] = mapped_column(ForeignKey("source_products.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    category: Mapped[str] = mapped_column(String(128), index=True)
    display_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    markup_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_hidden: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.utcnow,
    )


class InventoryItemModel(Base):
    __tablename__ = "inventory_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    catalog_product_id: Mapped[UUID] = mapped_column(ForeignKey("catalog_products.id"), index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    encrypted_content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True)
    reserved_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.utcnow,
    )
