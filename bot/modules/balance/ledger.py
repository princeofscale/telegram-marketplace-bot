from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum


class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    PURCHASE = "purchase"
    REFUND = "refund"
    ADMIN_EDIT = "admin_edit"
    REFERRAL_REWARD = "referral_reward"
    CHARGEBACK = "chargeback"


class InsufficientFundsError(ValueError):
    """Raised when a debit would make the user balance negative."""


@dataclass(frozen=True)
class LedgerEntry:
    amount: Decimal
    transaction_type: TransactionType
    balance_before: Decimal
    balance_after: Decimal
    comment: str


@dataclass
class BalanceLedger:
    balance: Decimal
    entries: list[LedgerEntry] = field(default_factory=list)

    @classmethod
    def opening(cls, balance: Decimal) -> BalanceLedger:
        return cls(balance=balance.quantize(Decimal("0.01")))

    def apply(self, amount: Decimal, transaction_type: TransactionType, comment: str = "") -> LedgerEntry:
        amount = amount.quantize(Decimal("0.01"))
        balance_before = self.balance
        balance_after = (balance_before + amount).quantize(Decimal("0.01"))

        if balance_after < Decimal("0.00"):
            msg = "insufficient_funds"
            raise InsufficientFundsError(msg)

        entry = LedgerEntry(
            amount=amount,
            transaction_type=transaction_type,
            balance_before=balance_before,
            balance_after=balance_after,
            comment=comment,
        )
        self.balance = balance_after
        self.entries.append(entry)
        return entry
