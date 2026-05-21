from __future__ import annotations
import asyncio
from decimal import Decimal

from loguru import logger

from bot.core.config import settings
from bot.database.database import sessionmaker
from bot.modules.security.inventory_crypto import InventoryCipher
from bot.services.lolz_market import LolzMarketClient
from bot.services.provider_sync import sync_lolz_market_items


async def main() -> None:
    if not settings.LOLZ_MARKET_ACCESS_TOKEN:
        msg = "LOLZ_MARKET_ACCESS_TOKEN is required"
        raise RuntimeError(msg)

    client = LolzMarketClient(
        access_token=settings.LOLZ_MARKET_ACCESS_TOKEN,
        base_url=settings.LOLZ_MARKET_BASE_URL,
    )
    async with sessionmaker() as session:
        result = await sync_lolz_market_items(
            session=session,
            client=client,
            categories=settings.lolz_market_categories,
            global_markup=Decimal("15.00"),
            cipher=InventoryCipher(settings.INVENTORY_ENCRYPTION_KEY),
            limit_per_category=settings.LOLZ_MARKET_SYNC_LIMIT_PER_CATEGORY,
        )
    logger.info(
        "lolz market sync completed | source_products={} catalog_products={} inventory_items={}",
        result.source_products,
        result.catalog_products,
        result.inventory_items,
    )


if __name__ == "__main__":
    asyncio.run(main())
