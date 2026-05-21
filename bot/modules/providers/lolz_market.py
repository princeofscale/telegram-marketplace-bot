from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

LOLZ_MARKET_SOURCE = "lolz_market"


@dataclass(frozen=True)
class LolzMarketItem:
    item_id: int
    title: str
    category: str
    price: Decimal
    payload: dict[str, Any]


@dataclass(frozen=True)
class LolzMarketPurchase:
    item_id: int
    raw_delivery: str
    payload: dict[str, Any]


def parse_lolz_market_item(raw_item: dict[str, Any], *, fallback_category: str = "unknown") -> LolzMarketItem:
    item_id = int(raw_item["item_id"])
    title = str(raw_item.get("title") or raw_item.get("item_title") or f"Lolz item #{item_id}")
    category = str(
        raw_item.get("category_name")
        or raw_item.get("category")
        or raw_item.get("category_url")
        or raw_item.get("categoryName")
        or fallback_category,
    )
    price = Decimal(str(raw_item.get("price") or "0")).quantize(Decimal("0.01"))
    return LolzMarketItem(
        item_id=item_id,
        title=title,
        category=category,
        price=price,
        payload=raw_item,
    )


def extract_lolz_delivery(raw_item: dict[str, Any]) -> str:
    login_data = raw_item.get("loginData")
    if isinstance(login_data, dict):
        for key in ("raw", "login_password", "loginPassword"):
            value = login_data.get(key)
            if value:
                return str(value)
        login = login_data.get("login")
        password = login_data.get("password")
        if login and password:
            return f"{login}:{password}"

    for key in ("accountData", "data", "information"):
        value = raw_item.get(key)
        if value:
            return str(value)

    return str(raw_item)
