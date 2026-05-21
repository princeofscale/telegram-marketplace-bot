from __future__ import annotations
from decimal import Decimal
from uuid import UUID

WALLET_CALLBACK = "wallet"
TOP_UP_CALLBACK = "top_up"
DEPOSIT_HISTORY_CALLBACK = "deposit_history"
DEPOSIT_DETAILS_CALLBACK_PREFIX = "deposit_info"
DEPOSIT_HISTORY_PAGE_CALLBACK_PREFIX = "deposit_history_page"
DEPOSIT_CALLBACK_PREFIX = "deposit"
CHECK_DEPOSIT_CALLBACK_PREFIX = "check_deposit"
DEPOSIT_METHOD_CALLBACK_PARTS = 3


def deposit_callback(amount: Decimal) -> str:
    return f"{DEPOSIT_CALLBACK_PREFIX}:{amount.quantize(Decimal('0.01'))}"


def deposit_method_callback(amount: Decimal, payment_method: str) -> str:
    return f"{DEPOSIT_CALLBACK_PREFIX}:{amount.quantize(Decimal('0.01'))}:{payment_method}"


def parse_deposit_callback(callback_data: str) -> Decimal:
    parts = callback_data.split(":")
    if len(parts) not in {2, 3} or parts[0] != DEPOSIT_CALLBACK_PREFIX:
        msg = "invalid_deposit_callback"
        raise ValueError(msg)
    amount = Decimal(parts[1]).quantize(Decimal("0.01"))
    if amount <= Decimal("0.00"):
        msg = "invalid_deposit_amount"
        raise ValueError(msg)
    return amount


def parse_deposit_method_callback(callback_data: str) -> tuple[Decimal, str | None]:
    amount = parse_deposit_callback(callback_data)
    parts = callback_data.split(":")
    payment_method = parts[2] if len(parts) == DEPOSIT_METHOD_CALLBACK_PARTS else None
    return amount, payment_method


def check_deposit_callback(provider_payment_id: str) -> str:
    return f"{CHECK_DEPOSIT_CALLBACK_PREFIX}:{provider_payment_id}"


def parse_check_deposit_callback(callback_data: str) -> str:
    prefix, _, provider_payment_id = callback_data.partition(":")
    if prefix != CHECK_DEPOSIT_CALLBACK_PREFIX or not provider_payment_id:
        msg = "invalid_check_deposit_callback"
        raise ValueError(msg)
    return provider_payment_id


def deposit_history_page_callback(page: int) -> str:
    return f"{DEPOSIT_HISTORY_PAGE_CALLBACK_PREFIX}:{page}"


def parse_deposit_history_page_callback(callback_data: str) -> int:
    prefix, _, raw_page = callback_data.partition(":")
    if prefix != DEPOSIT_HISTORY_PAGE_CALLBACK_PREFIX or not raw_page:
        msg = "invalid_deposit_history_page_callback"
        raise ValueError(msg)
    page = int(raw_page)
    if page < 0:
        msg = "invalid_deposit_history_page"
        raise ValueError(msg)
    return page


def deposit_details_callback(deposit_id: object) -> str:
    return f"{DEPOSIT_DETAILS_CALLBACK_PREFIX}:{deposit_id}"


def parse_deposit_details_callback(callback_data: str) -> UUID:
    prefix, _, raw_deposit_id = callback_data.partition(":")
    if prefix != DEPOSIT_DETAILS_CALLBACK_PREFIX or not raw_deposit_id:
        msg = "invalid_deposit_details_callback"
        raise ValueError(msg)
    return UUID(raw_deposit_id)
