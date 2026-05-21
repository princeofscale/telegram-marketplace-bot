from decimal import Decimal

import pytest

from bot.modules.balance.ledger import BalanceLedger, InsufficientFundsError, TransactionType


def test_ledger_records_deposits_and_purchases_without_direct_mutation() -> None:
    ledger = BalanceLedger.opening(balance=Decimal("0.00"))

    ledger.apply(amount=Decimal("100.00"), transaction_type=TransactionType.DEPOSIT, comment="test deposit")
    ledger.apply(amount=Decimal("-35.50"), transaction_type=TransactionType.PURCHASE, comment="order #1")

    assert ledger.balance == Decimal("64.50")
    assert [entry.balance_before for entry in ledger.entries] == [Decimal("0.00"), Decimal("100.00")]
    assert [entry.balance_after for entry in ledger.entries] == [Decimal("100.00"), Decimal("64.50")]


def test_ledger_rejects_purchase_that_would_make_balance_negative() -> None:
    ledger = BalanceLedger.opening(balance=Decimal("10.00"))

    with pytest.raises(InsufficientFundsError):
        ledger.apply(amount=Decimal("-10.01"), transaction_type=TransactionType.PURCHASE, comment="too much")
