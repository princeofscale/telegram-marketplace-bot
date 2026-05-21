from __future__ import annotations
from decimal import Decimal

from aiohttp import web
from loguru import logger

from bot.core.config import settings
from bot.database.database import sessionmaker
from bot.modules.payments.platega import PlategaCallback, PlategaStatus
from bot.services.payments import apply_platega_callback


async def platega_callback_handler(request: web.Request) -> web.Response:
    if request.headers.get("X-MerchantId") != settings.PLATEGA_MERCHANT_ID:
        raise web.HTTPUnauthorized
    if request.headers.get("X-Secret") != settings.PLATEGA_API_KEY:
        raise web.HTTPUnauthorized

    payload = await request.json()
    callback = PlategaCallback(
        transaction_id=str(payload["id"]),
        amount=Decimal(str(payload["amount"])).quantize(Decimal("0.01")),
        currency=str(payload.get("currency", "RUB")),
        status=PlategaStatus(str(payload["status"]).upper()),
        payment_method=payload.get("paymentMethod"),
    )

    async with sessionmaker() as session:
        status = await apply_platega_callback(session=session, callback=callback)

    logger.info(f"platega callback processed | transaction_id: {callback.transaction_id} | status: {status}")
    return web.Response(status=200)
