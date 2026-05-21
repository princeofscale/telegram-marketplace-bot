from __future__ import annotations
from decimal import Decimal
from urllib.parse import urlencode

LOLZ_BALANCE_PAYMENT_METHOD = "lolz_balance"
LOLZ_BALANCE_PAYMENT_TITLE = "LOLZ Balance"
LOLZ_TRANSFER_COMMENT_PREFIX = "lolz:"
LOLZ_TRANSFER_URL = "https://lzt.market/balance/transfer"


def build_lolz_transfer_comment(*, user_id: int, deposit_id: object) -> str:
    return f"{LOLZ_TRANSFER_COMMENT_PREFIX}{user_id}:{deposit_id}"


def build_lolz_transfer_link(
    *,
    username: str,
    amount: Decimal,
    comment: str,
    currency: str | None = None,
    hold: int = 0,
) -> str:
    params = {
        "username": username,
        "amount": str(amount.quantize(Decimal("0.01"))),
        "comment": comment,
        "hold": str(hold),
    }
    if currency:
        params["currency"] = currency
    return f"{LOLZ_TRANSFER_URL}?{urlencode(params)}"
