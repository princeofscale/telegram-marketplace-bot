from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from aiohttp import ClientSession

from bot.modules.payments.deposits import DepositStatus
from bot.modules.payments.platega import PlategaPaymentLink, PlategaPaymentLinkRequest, map_platega_status
from bot.modules.payments.provider import PaymentVerification


@dataclass(frozen=True)
class PlategaClient:
    merchant_id: str
    api_key: str
    base_url: str = "https://app.platega.io"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-MerchantId": self.merchant_id,
            "X-Secret": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_payment_link(
        self,
        *,
        request: PlategaPaymentLinkRequest,
    ) -> PlategaPaymentLink:
        body: dict[str, Any] = {
            "paymentDetails": {"amount": float(request.amount), "currency": "RUB"},
            "description": request.description,
            "return": request.return_url,
            "failedUrl": request.failed_url,
            "payload": request.payload,
        }
        if request.payment_method is not None:
            body["paymentMethod"] = int(request.payment_method)

        async with (
            ClientSession(headers=self.headers) as session,
            session.post(f"{self.base_url.rstrip('/')}/transaction/process", json=body) as response,
        ):
            response.raise_for_status()
            data = await response.json()

        payment_url = data.get("redirect") or data.get("url")
        transaction_id = data["transactionId"]
        return PlategaPaymentLink(
            transaction_id=transaction_id,
            payment_url=payment_url,
            status=map_platega_status(data.get("status", DepositStatus.PENDING.value)),
            payment_method=str(data.get("paymentMethod") or request.payment_method or "platega"),
        )

    async def verify_payment(self, provider_payment_id: str) -> PaymentVerification:
        async with (
            ClientSession(headers=self.headers) as session,
            session.get(f"{self.base_url.rstrip('/')}/transaction/{provider_payment_id}") as response,
        ):
            response.raise_for_status()
            data = await response.json()

        details = data.get("paymentDetails") or {}
        return PaymentVerification(
            provider_payment_id=str(data.get("id") or provider_payment_id),
            status=map_platega_status(data.get("status", DepositStatus.PENDING.value)),
            amount=Decimal(str(details.get("amount", "0"))).quantize(Decimal("0.01")),
        )
