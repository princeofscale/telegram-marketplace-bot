from __future__ import annotations
from uuid import UUID

PURCHASES_CALLBACK = "purchases"
ORDER_CALLBACK_PREFIX = "order"


def order_callback(order_id: UUID) -> str:
    return f"{ORDER_CALLBACK_PREFIX}:{order_id}"


def parse_order_callback(callback_data: str) -> UUID:
    prefix, _, raw_id = callback_data.partition(":")
    if prefix != ORDER_CALLBACK_PREFIX or not raw_id:
        msg = "invalid_order_callback"
        raise ValueError(msg)
    return UUID(raw_id)
