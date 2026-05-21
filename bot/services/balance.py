from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select

from bot.database.models import UserBalanceTransactionModel, UserModel
from bot.modules.audit.events import AuditAction, AuditEvent
from bot.modules.balance.ledger import BalanceLedger, TransactionType
from bot.services.audit import add_audit_log

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserNotFoundError(ValueError):
    """Raised when a balance transaction targets an unknown user."""


@dataclass(frozen=True)
class BalanceChange:
    balance_after: Decimal
    transaction: UserBalanceTransactionModel
    audit_event: AuditEvent
    total_deposited_delta: Decimal = Decimal("0.00")
    total_spent_delta: Decimal = Decimal("0.00")


@dataclass(frozen=True)
class BalanceTransactionRequest:
    user_id: int
    amount: Decimal
    transaction_type: TransactionType
    comment: str = ""


def build_balance_change(
    *,
    user_id: int,
    current_balance: Decimal,
    amount: Decimal,
    transaction_type: TransactionType,
    comment: str = "",
) -> BalanceChange:
    ledger = BalanceLedger.opening(balance=current_balance)
    entry = ledger.apply(amount=amount, transaction_type=transaction_type, comment=comment)

    transaction = UserBalanceTransactionModel(
        user_id=user_id,
        amount=entry.amount,
        type=entry.transaction_type.value,
        balance_before=entry.balance_before,
        balance_after=entry.balance_after,
        comment=entry.comment,
    )
    audit_event = AuditEvent(
        action=AuditAction.BALANCE_CHANGED,
        actor_id=user_id,
        target_id=str(user_id),
        payload={
            "amount": str(entry.amount),
            "balance_before": str(entry.balance_before),
            "balance_after": str(entry.balance_after),
            "transaction_type": entry.transaction_type.value,
            "comment": entry.comment,
        },
    )

    return BalanceChange(
        balance_after=entry.balance_after,
        transaction=transaction,
        audit_event=audit_event,
        total_deposited_delta=entry.amount if transaction_type == TransactionType.DEPOSIT else Decimal("0.00"),
        total_spent_delta=-entry.amount if transaction_type == TransactionType.PURCHASE else Decimal("0.00"),
    )


async def apply_balance_transaction(
    *,
    session: AsyncSession,
    request: BalanceTransactionRequest,
    commit: bool = True,
) -> BalanceChange:
    result = await session.execute(select(UserModel).where(UserModel.id == request.user_id).with_for_update())
    user = result.scalar_one_or_none()
    if user is None:
        msg = "user_not_found"
        raise UserNotFoundError(msg)

    change = build_balance_change(
        user_id=request.user_id,
        current_balance=user.balance,
        amount=request.amount,
        transaction_type=request.transaction_type,
        comment=request.comment,
    )
    user.balance = change.balance_after
    user.total_deposited += change.total_deposited_delta
    user.total_spent += change.total_spent_delta

    session.add(change.transaction)
    add_audit_log(session, change.audit_event)
    if commit:
        await session.commit()
    return change
