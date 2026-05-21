from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from bot.database.models import CatalogProductModel, InventoryItemModel, SourceProductModel
from bot.modules.catalog.pricing import MarkupPolicy, calculate_display_price
from bot.modules.inventory.statuses import InventoryStatus

if TYPE_CHECKING:
    from decimal import Decimal
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def build_catalog_product_from_source(
    source_product: SourceProductModel,
    *,
    global_markup: Decimal,
    category_markup: Decimal | None = None,
    product_markup: Decimal | None = None,
    title: str | None = None,
) -> CatalogProductModel:
    policy = MarkupPolicy(
        global_markup=global_markup,
        category_markup=category_markup,
        product_markup=product_markup,
    )
    return CatalogProductModel(
        source_product_id=source_product.id,
        title=title or source_product.raw_title,
        category=source_product.category,
        display_price=calculate_display_price(source_product.raw_price, policy),
        markup_percent=policy.effective_markup,
    )


async def list_available_catalog_products(*, session: AsyncSession) -> list[tuple[CatalogProductModel, int]]:
    result = await session.execute(
        select(CatalogProductModel, func.count(InventoryItemModel.id).label("available_count"))
        .join(InventoryItemModel, InventoryItemModel.catalog_product_id == CatalogProductModel.id)
        .where(
            CatalogProductModel.is_hidden.is_(False),
            InventoryItemModel.status == InventoryStatus.AVAILABLE.value,
        )
        .group_by(CatalogProductModel.id)
        .order_by(CatalogProductModel.category, CatalogProductModel.title),
    )
    return [(product, available_count) for product, available_count in result.all()]


async def get_visible_catalog_product(*, session: AsyncSession, product_id: UUID) -> CatalogProductModel | None:
    result = await session.execute(
        select(CatalogProductModel).where(
            CatalogProductModel.id == product_id,
            CatalogProductModel.is_hidden.is_(False),
        ),
    )
    return result.scalar_one_or_none()
