from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import select

from bot.database.models import DepositModel
from bot.modules.audit.events import AuditAction, AuditEvent
from bot.modules.balance.ledger import TransactionType
from bot.modules.payments.deposits import DepositStatus
from bot.modules.payments.lolz import (
    LOLZ_BALANCE_PAYMENT_METHOD,
    build_lolz_transfer_comment,
    build_lolz_transfer_link,
)
from bot.modules.payments.platega import (
    PLATEGA_PAYMENT_METHODS,
    PlategaCallback,
    PlategaPaymentLink,
    PlategaPaymentLinkRequest,
    PlategaPaymentMethod,
    build_platega_return_url,
    calculate_deposit_pricing,
    map_platega_status,
)
from bot.modules.payments.provider import PaymentVerification
from bot.services.audit import add_audit_log
from bot.services.balance import BalanceTransactionRequest, apply_balance_transaction

if TYPE_CHECKING:
    from typing import Protocol

    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.modules.payments.provider import PaymentProvider

    class PlategaPaymentProvider(Protocol):
        async def create_payment_link(self, *, request: PlategaPaymentLinkRequest) -> PlategaPaymentLink:
            """Create a payment link in Platega."""


@dataclass(frozen=True)
class VerifiedDepositUpdate:
    status: DepositStatus
    paid_amount: Decimal | None = None


@dataclass(frozen=True)
class PlategaDepositRequest:
    user_id: int
    amount: Decimal
    bot_public_url: str
    payment_method: PlategaPaymentMethod = PlategaPaymentMethod.SBP_QR


@dataclass(frozen=True)
class LolzBalanceDepositRequest:
    user_id: int
    amount: Decimal
    receiver_username: str
    currency: str | None = None


@dataclass(frozen=True)
class UserDepositsPage:
    deposits: list[DepositModel]
    has_next_page: bool


def build_provider_payment_id(*, user_id: int) -> str:
    return f"manual:{user_id}:{uuid4()}"


def build_platega_deposit_payload(*, deposit_id: object, user_id: int) -> str:
    return f"deposit:{deposit_id}:user:{user_id}"


async def create_manual_deposit(
    *,
    session: AsyncSession,
    user_id: int,
    amount: Decimal,
    payment_method: str = "manual",
) -> DepositModel:
    deposit = DepositModel(
        user_id=user_id,
        amount=amount.quantize(Decimal("0.01")),
        requested_amount=amount.quantize(Decimal("0.01")),
        commission_amount=Decimal("0.00"),
        payment_method=payment_method,
        provider_payment_id=build_provider_payment_id(user_id=user_id),
        status=DepositStatus.PENDING.value,
    )
    session.add(deposit)
    await session.flush()
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.DEPOSIT_CREATED,
            actor_id=user_id,
            target_id=str(deposit.id),
            payload={
                "amount": str(deposit.amount),
                "payment_method": deposit.payment_method,
                "provider_payment_id": deposit.provider_payment_id,
            },
        ),
    )
    await session.commit()
    return deposit


async def list_user_deposits(
    *,
    session: AsyncSession,
    user_id: int,
    page: int = 0,
    page_size: int = 5,
) -> UserDepositsPage:
    offset = page * page_size
    result = await session.execute(
        select(DepositModel)
        .where(DepositModel.user_id == user_id)
        .order_by(DepositModel.created_at.desc())
        .offset(offset)
        .limit(page_size + 1),
    )
    deposits = list(result.scalars())
    return UserDepositsPage(deposits=deposits[:page_size], has_next_page=len(deposits) > page_size)


async def get_user_deposit(*, session: AsyncSession, user_id: int, deposit_id: UUID) -> DepositModel:
    result = await session.execute(
        select(DepositModel).where(DepositModel.id == deposit_id, DepositModel.user_id == user_id),
    )
    return result.scalar_one()


async def create_platega_deposit(
    *,
    session: AsyncSession,
    provider: PlategaPaymentProvider,
    request: PlategaDepositRequest,
) -> DepositModel:
    pricing = calculate_deposit_pricing(
        balance_amount=request.amount,
        policy=PLATEGA_PAYMENT_METHODS[request.payment_method],
    )
    deposit = DepositModel(
        user_id=request.user_id,
        amount=pricing.balance_amount,
        requested_amount=pricing.payment_amount,
        commission_amount=pricing.commission_amount,
        payment_method=request.payment_method.value,
        provider_payment_id=build_provider_payment_id(user_id=request.user_id),
        status=DepositStatus.PENDING.value,
    )
    session.add(deposit)
    await session.flush()

    payment_link: PlategaPaymentLink = await provider.create_payment_link(
        request=PlategaPaymentLinkRequest(
            amount=deposit.requested_amount,
            description=f"VoxMarket balance top-up {deposit.id}",
            return_url=build_platega_return_url(bot_public_url=request.bot_public_url, deposit_id=deposit.id),
            failed_url=build_platega_return_url(
                bot_public_url=request.bot_public_url,
                deposit_id=deposit.id,
                success=False,
            ),
            payload=build_platega_deposit_payload(deposit_id=deposit.id, user_id=request.user_id),
            payment_method=pricing.provider_method_id,
        ),
    )

    deposit.provider_payment_id = payment_link.transaction_id
    deposit.payment_method = payment_link.payment_method
    deposit.payment_url = payment_link.payment_url
    deposit.status = payment_link.status.value
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.DEPOSIT_CREATED,
            actor_id=request.user_id,
            target_id=str(deposit.id),
            payload={
                "amount": str(deposit.amount),
                "requested_amount": str(deposit.requested_amount),
                "commission_amount": str(deposit.commission_amount),
                "payment_method": deposit.payment_method,
                "provider_payment_id": deposit.provider_payment_id,
            },
        ),
    )
    await session.commit()
    return deposit


async def create_lolz_balance_deposit(
    *,
    session: AsyncSession,
    request: LolzBalanceDepositRequest,
) -> DepositModel:
    deposit_id = uuid4()
    amount = request.amount.quantize(Decimal("0.01"))
    provider_payment_id = build_lolz_transfer_comment(user_id=request.user_id, deposit_id=deposit_id.hex)
    deposit = DepositModel(
        id=deposit_id,
        user_id=request.user_id,
        amount=amount,
        requested_amount=amount,
        commission_amount=Decimal("0.00"),
        payment_method=LOLZ_BALANCE_PAYMENT_METHOD,
        provider_payment_id=provider_payment_id,
        payment_url=build_lolz_transfer_link(
            username=request.receiver_username,
            amount=amount,
            comment=provider_payment_id,
            currency=request.currency,
        ),
        status=DepositStatus.PENDING.value,
    )
    session.add(deposit)
    await session.flush()
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.DEPOSIT_CREATED,
            actor_id=request.user_id,
            target_id=str(deposit.id),
            payload={
                "amount": str(deposit.amount),
                "requested_amount": str(deposit.requested_amount),
                "commission_amount": str(deposit.commission_amount),
                "payment_method": deposit.payment_method,
                "provider_payment_id": deposit.provider_payment_id,
            },
        ),
    )
    await session.commit()
    return deposit


def build_verified_deposit_update(
    *,
    expected_amount: Decimal,
    expected_provider_payment_id: str,
    verification: PaymentVerification,
) -> VerifiedDepositUpdate:
    if verification.provider_payment_id != expected_provider_payment_id:
        return VerifiedDepositUpdate(status=DepositStatus.FAILED)

    if verification.status != DepositStatus.PAID:
        return VerifiedDepositUpdate(status=verification.status)

    if verification.amount.quantize(Decimal("0.01")) < expected_amount.quantize(Decimal("0.01")):
        return VerifiedDepositUpdate(status=DepositStatus.FAILED)

    return VerifiedDepositUpdate(status=DepositStatus.PAID, paid_amount=verification.amount.quantize(Decimal("0.01")))


async def verify_deposit_with_provider(
    *,
    session: AsyncSession,
    provider: PaymentProvider,
    provider_payment_id: str,
    user_id: int | None = None,
) -> VerifiedDepositUpdate:
    conditions = [DepositModel.provider_payment_id == provider_payment_id]
    if user_id is not None:
        conditions.append(DepositModel.user_id == user_id)
    result = await session.execute(select(DepositModel).where(*conditions))
    deposit = result.scalar_one()
    verification = await provider.verify_payment(provider_payment_id)
    update = build_verified_deposit_update(
        expected_amount=deposit.requested_amount,
        expected_provider_payment_id=deposit.provider_payment_id,
        verification=verification,
    )

    previous_status = deposit.status
    deposit.status = update.status.value
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.DEPOSIT_VERIFIED,
            actor_id=deposit.user_id,
            target_id=str(deposit.id),
            payload={"status": update.status.value, "provider_payment_id": deposit.provider_payment_id},
        ),
    )
    if update.status == DepositStatus.PAID and update.paid_amount is not None:
        if previous_status == DepositStatus.PAID.value:
            await session.commit()
            return update
        deposit.paid_at = datetime.now(UTC).replace(tzinfo=None)
        await apply_balance_transaction(
            session=session,
            request=BalanceTransactionRequest(
                user_id=deposit.user_id,
                amount=deposit.amount,
                transaction_type=TransactionType.DEPOSIT,
                comment=f"deposit:{deposit.provider_payment_id}",
            ),
        )
    else:
        await session.commit()

    return update


async def apply_platega_callback(*, session: AsyncSession, callback: PlategaCallback) -> DepositStatus:
    result = await session.execute(
        select(DepositModel).where(DepositModel.provider_payment_id == callback.transaction_id).with_for_update(),
    )
    deposit = result.scalar_one()
    status = map_platega_status(callback.status)

    if status == DepositStatus.PAID:
        if deposit.status == DepositStatus.PAID.value:
            await session.commit()
            return status
        update = build_verified_deposit_update(
            expected_amount=deposit.requested_amount,
            expected_provider_payment_id=deposit.provider_payment_id,
            verification=PaymentVerification(
                provider_payment_id=callback.transaction_id,
                status=status,
                amount=callback.amount,
            ),
        )
        if update.status == DepositStatus.PAID and update.paid_amount is not None:
            deposit.status = update.status.value
            deposit.paid_at = datetime.now(UTC).replace(tzinfo=None)
            await apply_balance_transaction(
                session=session,
                request=BalanceTransactionRequest(
                    user_id=deposit.user_id,
                    amount=deposit.amount,
                    transaction_type=TransactionType.DEPOSIT,
                    comment=f"deposit:{deposit.provider_payment_id}",
                ),
                commit=False,
            )
        else:
            deposit.status = update.status.value
    else:
        deposit.status = status.value

    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.DEPOSIT_VERIFIED,
            actor_id=deposit.user_id,
            target_id=str(deposit.id),
            payload={"status": deposit.status, "provider_payment_id": deposit.provider_payment_id},
        ),
    )
    await session.commit()
    return status
