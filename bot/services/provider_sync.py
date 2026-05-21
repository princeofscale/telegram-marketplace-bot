from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import select

from bot.database.models import CatalogProductModel, InventoryItemModel, SourceProductModel
from bot.modules.inventory.statuses import InventoryStatus
from bot.modules.providers.lolz_market import LOLZ_MARKET_SOURCE, LolzMarketItem
from bot.services.catalog import build_catalog_product_from_source

if TYPE_CHECKING:
    from decimal import Decimal

    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.modules.security.inventory_crypto import InventoryCipher
    from bot.services.lolz_market import LolzMarketClient


@dataclass(frozen=True)
class ProviderSyncResult:
    source_products: int = 0
    catalog_products: int = 0
    inventory_items: int = 0


async def sync_lolz_market_items(  # noqa: PLR0913
    *,
    session: AsyncSession,
    client: LolzMarketClient,
    categories: tuple[str, ...],
    global_markup: Decimal,
    cipher: InventoryCipher,
    limit_per_category: int,
) -> ProviderSyncResult:
    result = ProviderSyncResult()
    for category in categories:
        items = await client.list_items(category=category, limit=limit_per_category)
        for item in items:
            result = await upsert_lolz_market_item(
                session=session,
                item=item,
                global_markup=global_markup,
                cipher=cipher,
                result=result,
            )

    await session.commit()
    return result


async def upsert_lolz_market_item(
    *,
    session: AsyncSession,
    item: LolzMarketItem,
    global_markup: Decimal,
    cipher: InventoryCipher,
    result: ProviderSyncResult | None = None,
) -> ProviderSyncResult:
    result = result or ProviderSyncResult()
    source_product = await get_source_product(session=session, source_item_id=str(item.item_id))
    if source_product is None:
        source_product = SourceProductModel(
            source=LOLZ_MARKET_SOURCE,
            source_item_id=str(item.item_id),
            raw_title=item.title,
            raw_price=item.price,
            category=item.category,
            payload=item.payload,
        )
        session.add(source_product)
        await session.flush()
        result = ProviderSyncResult(
            source_products=result.source_products + 1,
            catalog_products=result.catalog_products,
            inventory_items=result.inventory_items,
        )
    else:
        source_product.raw_title = item.title
        source_product.raw_price = item.price
        source_product.category = item.category
        source_product.payload = item.payload

    catalog_product = await get_catalog_product(session=session, source_product=source_product)
    if catalog_product is None:
        catalog_product = build_catalog_product_from_source(source_product, global_markup=global_markup)
        session.add(catalog_product)
        await session.flush()
        result = ProviderSyncResult(
            source_products=result.source_products,
            catalog_products=result.catalog_products + 1,
            inventory_items=result.inventory_items,
        )
    else:
        catalog_product.title = source_product.raw_title
        catalog_product.category = source_product.category
        catalog_product.display_price = build_catalog_product_from_source(
            source_product,
            global_markup=global_markup,
        ).display_price

    if not await has_active_inventory_item(session=session, catalog_product=catalog_product):
        session.add(
            InventoryItemModel(
                catalog_product_id=catalog_product.id,
                source=LOLZ_MARKET_SOURCE,
                encrypted_content=cipher.encrypt(f"lolz_market_item:{item.item_id}"),
                status=InventoryStatus.AVAILABLE.value,
            ),
        )
        await session.flush()
        result = ProviderSyncResult(
            source_products=result.source_products,
            catalog_products=result.catalog_products,
            inventory_items=result.inventory_items + 1,
        )

    return result


async def get_source_product(*, session: AsyncSession, source_item_id: str) -> SourceProductModel | None:
    result = await session.execute(
        select(SourceProductModel).where(
            SourceProductModel.source == LOLZ_MARKET_SOURCE,
            SourceProductModel.source_item_id == source_item_id,
        ),
    )
    return result.scalar_one_or_none()


async def get_catalog_product(
    *,
    session: AsyncSession,
    source_product: SourceProductModel,
) -> CatalogProductModel | None:
    result = await session.execute(
        select(CatalogProductModel).where(CatalogProductModel.source_product_id == source_product.id),
    )
    return result.scalar_one_or_none()


async def has_active_inventory_item(*, session: AsyncSession, catalog_product: CatalogProductModel) -> bool:
    result = await session.execute(
        select(InventoryItemModel.id)
        .where(
            InventoryItemModel.catalog_product_id == catalog_product.id,
            InventoryItemModel.source == LOLZ_MARKET_SOURCE,
            InventoryItemModel.status.in_({InventoryStatus.AVAILABLE.value, InventoryStatus.RESERVED.value}),
        )
        .limit(1),
    )
    return result.scalar_one_or_none() is not None
