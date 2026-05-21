from decimal import Decimal

from bot.modules.audit.events import AuditAction
from bot.modules.balance.ledger import TransactionType
from bot.services.balance import build_balance_change

USER_ID = 42


def test_build_balance_change_creates_ledger_row_and_audit_event() -> None:
    change = build_balance_change(
        user_id=USER_ID,
        current_balance=Decimal("10.00"),
        amount=Decimal("15.25"),
        transaction_type=TransactionType.DEPOSIT,
        comment="manual test",
    )

    assert change.balance_after == Decimal("25.25")
    assert change.transaction.user_id == USER_ID
    assert change.transaction.amount == Decimal("15.25")
    assert change.transaction.balance_before == Decimal("10.00")
    assert change.transaction.balance_after == Decimal("25.25")
    assert change.audit_event.action == AuditAction.BALANCE_CHANGED
    assert change.audit_event.payload["transaction_type"] == "deposit"


def test_build_balance_change_tracks_purchase_spend_delta() -> None:
    change = build_balance_change(
        user_id=USER_ID,
        current_balance=Decimal("50.00"),
        amount=Decimal("-12.30"),
        transaction_type=TransactionType.PURCHASE,
        comment="order",
    )

    assert change.balance_after == Decimal("37.70")
    assert change.total_deposited_delta == Decimal("0.00")
    assert change.total_spent_delta == Decimal("12.30")
