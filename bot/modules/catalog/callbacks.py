from __future__ import annotations
from uuid import UUID

CATALOG_CALLBACK = "catalog"
PRODUCT_CALLBACK_PREFIX = "product"
CONFIRM_BUY_CALLBACK_PREFIX = "confirm_buy"
BUY_CALLBACK_PREFIX = "buy"


def product_callback(product_id: UUID) -> str:
    return f"{PRODUCT_CALLBACK_PREFIX}:{product_id}"


def confirm_buy_callback(product_id: UUID) -> str:
    return f"{CONFIRM_BUY_CALLBACK_PREFIX}:{product_id}"


def buy_callback(product_id: UUID) -> str:
    return f"{BUY_CALLBACK_PREFIX}:{product_id}"


def parse_product_callback(callback_data: str, *, prefix: str) -> UUID:
    raw_prefix, _, raw_id = callback_data.partition(":")
    if raw_prefix != prefix or not raw_id:
        msg = "invalid_catalog_callback"
        raise ValueError(msg)
    return UUID(raw_id)
