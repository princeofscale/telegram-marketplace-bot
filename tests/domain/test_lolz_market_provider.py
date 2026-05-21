from decimal import Decimal
from typing import Any

from bot.modules.providers.lolz_market import extract_lolz_delivery, parse_lolz_market_item
from bot.services.lolz_market import LolzMarketClient

LOLZ_ITEM_ID = 123


def test_lolz_market_item_parser_normalizes_market_payload() -> None:
    item = parse_lolz_market_item(
        {
            "item_id": LOLZ_ITEM_ID,
            "title": "Telegram Stars",
            "category_name": "telegram",
            "price": 100,
        },
    )

    assert item.item_id == LOLZ_ITEM_ID
    assert item.title == "Telegram Stars"
    assert item.category == "telegram"
    assert item.price == Decimal("100.00")


def test_lolz_market_delivery_prefers_raw_login_data() -> None:
    assert extract_lolz_delivery({"loginData": {"raw": "login:password"}}) == "login:password"


def test_lolz_market_client_uses_bearer_token_header() -> None:
    client = LolzMarketClient(access_token="test-access-token")  # noqa: S106

    assert client.headers["Authorization"] == "Bearer test-access-token"


async def test_lolz_market_client_uses_lolzteam_market_wrapper() -> None:
    fake_market = FakeMarket()
    client = LolzMarketClient(
        access_token="header.payload.signature",  # noqa: S106
        base_url="https://prod-api.lzt.market",
        market_factory=lambda **_: fake_market,
    )

    item = await client.list_items(category="telegram", limit=1)
    purchase = await client.reserve_check_confirm_buy(item_id=LOLZ_ITEM_ID, price=Decimal("100.00"))

    assert item[0].item_id == LOLZ_ITEM_ID
    assert purchase.raw_delivery == "login:password"
    assert fake_market.calls == [
        ("categories.get", {"category_name": "telegram", "page": 1}),
        ("cart.add", {"item_id": LOLZ_ITEM_ID}),
        ("purchasing.check", {"item_id": LOLZ_ITEM_ID}),
        ("purchasing.buy", {"item_id": LOLZ_ITEM_ID, "price": 100.0}),
    ]


class FakeResponse:
    status_code = 200
    text = "{}"

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def json(self) -> dict[str, Any]:
        return self._payload


class FakeMarket:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.categories = FakeCategories(self)
        self.purchasing = FakePurchasing(self)
        self.managing = FakeManaging()
        self.settings = FakeSettings()


class FakeSettings:
    base_url = ""


class FakeCategories:
    def __init__(self, market: FakeMarket) -> None:
        self._market = market

    async def get(self, **kwargs: Any) -> FakeResponse:
        self._market.calls.append(("categories.get", kwargs))
        return FakeResponse(
            {
                "items": [
                    {
                        "item_id": LOLZ_ITEM_ID,
                        "title": "Telegram Stars",
                        "category": "telegram",
                        "price": 100,
                    },
                ],
            },
        )


class FakeManaging:
    async def get(self, *, item_id: int) -> FakeResponse:
        return FakeResponse({"item": {"item_id": item_id, "price": 100}})


class FakePurchasing:
    def __init__(self, market: FakeMarket) -> None:
        self._market = market
        self.cart = FakeCart(market)

    async def check(self, **kwargs: Any) -> FakeResponse:
        self._market.calls.append(("purchasing.check", kwargs))
        return FakeResponse({"status": "ok"})

    async def buy(self, **kwargs: Any) -> FakeResponse:
        self._market.calls.append(("purchasing.buy", kwargs))
        return FakeResponse(
            {"status": "ok", "item": {"item_id": kwargs["item_id"], "loginData": {"raw": "login:password"}}},
        )


class FakeCart:
    def __init__(self, market: FakeMarket) -> None:
        self._market = market

    async def add(self, **kwargs: Any) -> FakeResponse:
        self._market.calls.append(("cart.add", kwargs))
        return FakeResponse({"status": "ok"})
