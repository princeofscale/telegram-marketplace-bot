from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Protocol

from LOLZTEAM.Client import Market

from bot.modules.payments.deposits import DepositStatus
from bot.modules.payments.provider import PaymentVerification

if TYPE_CHECKING:
    from collections.abc import Callable

HTTP_BAD_REQUEST = 400


class LolzPaymentApiError(RuntimeError):
    """Raised when the Lolz payment API returns an error response."""


class LolzPaymentResponse(Protocol):
    status_code: int
    text: str

    def json(self) -> dict[str, Any]: ...


class LolzPaymentApi(Protocol):
    payments: Any
    settings: Any


class LolzBalanceClient:
    def __init__(
        self,
        *,
        access_token: str,
        base_url: str = "https://prod-api.lzt.market",
        timeout_seconds: int = 30,
        market_factory: Callable[..., LolzPaymentApi] | None = None,
    ) -> None:
        self._access_token = access_token
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._market_factory = market_factory
        self._market: LolzPaymentApi | None = None

    @property
    def market(self) -> LolzPaymentApi:
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

    def _parse_response(self, response: LolzPaymentResponse, *, action: str) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            msg = f"invalid_lolz_payment_response:{action}:{response.status_code}:{response.text[:200]}"
            raise LolzPaymentApiError(msg) from exc

        if response.status_code >= HTTP_BAD_REQUEST:
            msg = f"lolz_payment_http_error:{action}:{response.status_code}:{payload}"
            raise LolzPaymentApiError(msg)
        if payload.get("status") not in {None, "ok"} and "errors" in payload:
            msg = f"lolz_payment_api_error:{action}:{payload}"
            raise LolzPaymentApiError(msg)
        return payload

    async def verify_payment(self, provider_payment_id: str) -> PaymentVerification:
        response = await self.market.payments.history(
            operation_type="income",
            comment=provider_payment_id,
            page=1,
        )
        payload = self._parse_response(response, action="verify_payment")
        payment = find_lolz_income_payment(payload=payload, comment=provider_payment_id)
        if payment is None:
            return PaymentVerification(
                provider_payment_id=provider_payment_id,
                status=DepositStatus.PENDING,
                amount=Decimal("0.00"),
            )

        return PaymentVerification(
            provider_payment_id=provider_payment_id,
            status=DepositStatus.PAID,
            amount=extract_lolz_payment_amount(payment),
        )


def find_lolz_income_payment(*, payload: dict[str, Any], comment: str) -> dict[str, Any] | None:
    raw_payments = payload.get("payments") or payload.get("items") or payload.get("data") or []
    if isinstance(raw_payments, dict):
        raw_payments = raw_payments.values()

    for payment in raw_payments:
        if not isinstance(payment, dict):
            continue
        if str(payment.get("comment") or payment.get("description") or "") != comment:
            continue
        if is_lolz_payment_on_hold(payment):
            continue
        return payment
    return None


def is_lolz_payment_on_hold(payment: dict[str, Any]) -> bool:
    value = payment.get("hold") or payment.get("is_hold") or payment.get("transfer_hold")
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


def extract_lolz_payment_amount(payment: dict[str, Any]) -> Decimal:
    raw_amount = payment.get("amount") or payment.get("incoming_sum") or payment.get("sum") or "0"
    return Decimal(str(raw_amount)).quantize(Decimal("0.01"))
