from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from bot.modules.payments.deposits import DepositStatus

if TYPE_CHECKING:
    from uuid import UUID


class PlategaPaymentMethod(StrEnum):
    SBP_QR = "sbp_qr"
    CRYPTO = "crypto"


class CommissionPayer(StrEnum):
    MERCHANT = "merchant"
    CLIENT = "client"


class PlategaStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    CHARGEBACKED = "CHARGEBACKED"


@dataclass(frozen=True)
class PaymentMethodPolicy:
    method: PlategaPaymentMethod
    title: str
    commission_percent: Decimal
    provider_method_id: int | None = None
    commission_payer: CommissionPayer = CommissionPayer.CLIENT


@dataclass(frozen=True)
class DepositPricing:
    balance_amount: Decimal
    payment_amount: Decimal
    commission_amount: Decimal
    commission_percent: Decimal
    commission_payer: CommissionPayer
    payment_method: PlategaPaymentMethod
    provider_method_id: int | None


PLATEGA_PAYMENT_METHODS = {
    PlategaPaymentMethod.SBP_QR: PaymentMethodPolicy(
        method=PlategaPaymentMethod.SBP_QR,
        title="SBP QR",
        commission_percent=Decimal("10.00"),
        provider_method_id=2,
    ),
    PlategaPaymentMethod.CRYPTO: PaymentMethodPolicy(
        method=PlategaPaymentMethod.CRYPTO,
        title="Crypto",
        commission_percent=Decimal("4.00"),
        provider_method_id=13,
    ),
}


def calculate_deposit_pricing(*, balance_amount: Decimal, policy: PaymentMethodPolicy) -> DepositPricing:
    balance_amount = balance_amount.quantize(Decimal("0.01"))
    commission_amount = (balance_amount * policy.commission_percent / Decimal(100)).quantize(Decimal("0.01"))
    payment_amount = (
        balance_amount + commission_amount if policy.commission_payer == CommissionPayer.CLIENT else balance_amount
    )
    return DepositPricing(
        balance_amount=balance_amount,
        payment_amount=payment_amount,
        commission_amount=commission_amount,
        commission_percent=policy.commission_percent,
        commission_payer=policy.commission_payer,
        payment_method=policy.method,
        provider_method_id=policy.provider_method_id,
    )


@dataclass(frozen=True)
class PlategaPaymentLink:
    transaction_id: str
    payment_url: str
    status: DepositStatus
    payment_method: str


@dataclass(frozen=True)
class PlategaPaymentLinkRequest:
    amount: Decimal
    description: str
    return_url: str
    failed_url: str
    payload: str
    payment_method: int | None = None


@dataclass(frozen=True)
class PlategaCallback:
    transaction_id: str
    amount: Decimal
    currency: str
    status: PlategaStatus
    payment_method: int | None = None


def build_platega_return_url(*, bot_public_url: str, deposit_id: UUID, success: bool = True) -> str:
    suffix = "deposit" if success else "deposit_failed"
    return f"{bot_public_url}?start={suffix}_{deposit_id.hex}"


def map_platega_status(status: str) -> DepositStatus:
    match status.upper():
        case PlategaStatus.CONFIRMED:
            return DepositStatus.PAID
        case PlategaStatus.CANCELED:
            return DepositStatus.CANCELLED
        case PlategaStatus.CHARGEBACKED:
            return DepositStatus.FAILED
        case _:
            return DepositStatus.PENDING
