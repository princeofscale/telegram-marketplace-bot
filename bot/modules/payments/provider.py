from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from decimal import Decimal

    from bot.modules.payments.deposits import DepositStatus


@dataclass(frozen=True)
class PaymentVerification:
    provider_payment_id: str
    status: DepositStatus
    amount: Decimal


class PaymentProvider(Protocol):
    async def verify_payment(self, provider_payment_id: str) -> PaymentVerification:
        """Fetch trusted payment state from the provider API."""
