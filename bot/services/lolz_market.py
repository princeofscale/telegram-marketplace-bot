from __future__ import annotations
from typing import TYPE_CHECKING, Any, Protocol

from LOLZTEAM.Client import Market

from bot.modules.providers.lolz_market import (
    LolzMarketItem,
    LolzMarketPurchase,
    extract_lolz_delivery,
    parse_lolz_market_item,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from decimal import Decimal

HTTP_BAD_REQUEST = 400


class LolzMarketApiError(RuntimeError):
    """Raised when the Lolz Market API returns an error response."""


class LolzMarketResponse(Protocol):
    status_code: int
    text: str

    def json(self) -> dict[str, Any]: ...


class LolzMarketApi(Protocol):
    categories: Any
    managing: Any
    purchasing: Any
    settings: Any


class LolzMarketClient:
    def __init__(
        self,
        *,
        access_token: str,
        base_url: str = "https://prod-api.lzt.market",
        timeout_seconds: int = 30,
        market_factory: Callable[..., LolzMarketApi] | None = None,
    ) -> None:
        self._access_token = access_token
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._market_factory = market_factory
        self._market: LolzMarketApi | None = None

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }

    @property
    def market(self) -> LolzMarketApi:
        if self._market is None:
            if self._market_factory is None:
                self._market_factory = Market
            self._market = self._market_factory(
                token=self._access_token,
                language="en",
                timeout=self._timeout_seconds,
            )
            self._market.settings.base_url = self._base_url
            if hasattr(self._market.settings, "async_client"):
                self._market.settings.async_client.base_url = self._base_url
        return self._market

    def _parse_response(self, response: LolzMarketResponse, *, action: str) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            msg = f"invalid_lolz_market_response:{action}:{response.status_code}:{response.text[:200]}"
            raise LolzMarketApiError(msg) from exc

        if response.status_code >= HTTP_BAD_REQUEST:
            msg = f"lolz_market_http_error:{action}:{response.status_code}:{payload}"
            raise LolzMarketApiError(msg)
        if payload.get("status") not in {None, "ok"} and "errors" in payload:
            msg = f"lolz_market_api_error:{action}:{payload}"
            raise LolzMarketApiError(msg)
        return payload

    async def list_items(
        self,
        *,
        category: str,
        page: int = 1,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[LolzMarketItem]:
        request_params = {"page": page, **(params or {})}
        response = await self.market.categories.get(category_name=category, **request_params)
        payload = self._parse_response(response, action="list_items")
        raw_items = payload.get("items") or []
        items = [parse_lolz_market_item(raw_item, fallback_category=category) for raw_item in raw_items]
        return items[:limit] if limit is not None else items

    async def get_item(self, item_id: int) -> LolzMarketItem:
        response = await self.market.managing.get(item_id=item_id)
        payload = self._parse_response(response, action="get_item")
        return parse_lolz_market_item(payload["item"])

    async def reserve_item(self, *, item_id: int) -> dict[str, Any]:
        response = await self.market.purchasing.cart.add(item_id=item_id)
        return self._parse_response(response, action="reserve_item")

    async def check_item(self, *, item_id: int) -> dict[str, Any]:
        response = await self.market.purchasing.check(item_id=item_id)
        return self._parse_response(response, action="check_item")

    async def confirm_buy(self, *, item_id: int, price: Decimal) -> LolzMarketPurchase:
        response = await self.market.purchasing.buy(item_id=item_id, price=float(price))
        payload = self._parse_response(response, action="confirm_buy")
        raw_item = payload["item"]
        return LolzMarketPurchase(
            item_id=item_id,
            raw_delivery=extract_lolz_delivery(raw_item),
            payload=payload,
        )

    async def reserve_check_confirm_buy(self, *, item_id: int, price: Decimal) -> LolzMarketPurchase:
        await self.reserve_item(item_id=item_id)
        await self.check_item(item_id=item_id)
        return await self.confirm_buy(item_id=item_id, price=price)
