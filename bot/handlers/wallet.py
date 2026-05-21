from __future__ import annotations
from html import escape
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _
from sqlalchemy.exc import NoResultFound

from bot.core.config import settings
from bot.keyboards.inline.wallet import (
    deposit_history_keyboard,
    deposit_method_keyboard,
    deposit_payment_keyboard,
    top_up_keyboard,
    wallet_keyboard,
)
from bot.modules.payments.callbacks import (
    CHECK_DEPOSIT_CALLBACK_PREFIX,
    DEPOSIT_CALLBACK_PREFIX,
    DEPOSIT_DETAILS_CALLBACK_PREFIX,
    DEPOSIT_HISTORY_CALLBACK,
    DEPOSIT_HISTORY_PAGE_CALLBACK_PREFIX,
    TOP_UP_CALLBACK,
    WALLET_CALLBACK,
    parse_check_deposit_callback,
    parse_deposit_details_callback,
    parse_deposit_history_page_callback,
    parse_deposit_method_callback,
)
from bot.modules.payments.deposits import DepositStatus
from bot.modules.payments.lolz import LOLZ_BALANCE_PAYMENT_METHOD, LOLZ_TRANSFER_COMMENT_PREFIX
from bot.modules.payments.platega import PlategaPaymentMethod
from bot.services.lolz_payments import LolzBalanceClient, LolzPaymentApiError
from bot.services.payments import (
    LolzBalanceDepositRequest,
    PlategaDepositRequest,
    create_lolz_balance_deposit,
    create_manual_deposit,
    create_platega_deposit,
    get_user_deposit,
    list_user_deposits,
    verify_deposit_with_provider,
)
from bot.services.platega import PlategaClient
from bot.services.users import get_user
from bot.utils.messages import send_section_message

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router(name="wallet")


@router.callback_query(F.data == WALLET_CALLBACK)
async def wallet_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if callback_query.message and callback_query.from_user:
        await send_wallet(callback_query.message, session=session, user_id=callback_query.from_user.id, edit=True)
    await callback_query.answer()


@router.callback_query(F.data == TOP_UP_CALLBACK)
async def top_up_callback_handler(callback_query: types.CallbackQuery) -> None:
    if callback_query.message:
        await send_section_message(
            callback_query.message,
            _("top up title"),
            section="profile",
            reply_markup=top_up_keyboard(),
            edit=True,
        )
    await callback_query.answer()


@router.callback_query(F.data == DEPOSIT_HISTORY_CALLBACK)
async def deposit_history_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if callback_query.message and callback_query.from_user:
        await send_deposit_history(callback_query.message, session=session, user_id=callback_query.from_user.id)
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{DEPOSIT_HISTORY_PAGE_CALLBACK_PREFIX}:"))
async def deposit_history_page_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.message or not callback_query.from_user:
        await callback_query.answer(_("deposit unavailable"))
        return
    try:
        page = parse_deposit_history_page_callback(callback_query.data)
    except ValueError:
        await callback_query.answer(_("deposit unavailable"), show_alert=True)
        return
    await send_deposit_history(
        callback_query.message,
        session=session,
        user_id=callback_query.from_user.id,
        page=page,
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{DEPOSIT_CALLBACK_PREFIX}:"))
async def deposit_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.from_user or not callback_query.message:
        await callback_query.answer(_("wallet unavailable"))
        return

    try:
        amount, payment_method_code = parse_deposit_method_callback(callback_query.data)
    except (ValueError, ArithmeticError):
        await callback_query.answer(_("deposit unavailable"), show_alert=True)
        return

    platega_enabled = bool(settings.PLATEGA_MERCHANT_ID and settings.PLATEGA_API_KEY)
    lolz_balance_enabled = bool(settings.LOLZ_MARKET_ACCESS_TOKEN and settings.LOLZ_BALANCE_USERNAME)
    if payment_method_code is None:
        await send_section_message(
            callback_query.message,
            _("choose payment method").format(amount=amount),
            section="profile",
            reply_markup=deposit_method_keyboard(
                amount,
                include_platega=platega_enabled,
                include_lolz_balance=lolz_balance_enabled,
            ),
            edit=True,
        )
        await callback_query.answer()
        return

    if payment_method_code == LOLZ_BALANCE_PAYMENT_METHOD:
        if not lolz_balance_enabled:
            await callback_query.answer(_("deposit check unavailable"), show_alert=True)
            return
        deposit = await create_lolz_balance_deposit(
            session=session,
            request=LolzBalanceDepositRequest(
                user_id=callback_query.from_user.id,
                amount=amount,
                receiver_username=settings.LOLZ_BALANCE_USERNAME,
                currency=settings.LOLZ_BALANCE_CURRENCY,
            ),
        )
    elif platega_enabled:
        try:
            platega_payment_method = PlategaPaymentMethod(payment_method_code)
        except ValueError:
            await callback_query.answer(_("deposit unavailable"), show_alert=True)
            return
        deposit = await create_platega_deposit(
            session=session,
            provider=PlategaClient(
                merchant_id=settings.PLATEGA_MERCHANT_ID,
                api_key=settings.PLATEGA_API_KEY,
                base_url=settings.PLATEGA_BASE_URL,
            ),
            request=PlategaDepositRequest(
                user_id=callback_query.from_user.id,
                amount=amount,
                bot_public_url=settings.BOT_PUBLIC_URL,
                payment_method=platega_payment_method,
            ),
        )
    else:
        deposit = await create_manual_deposit(session=session, user_id=callback_query.from_user.id, amount=amount)

    reply_markup = (
        deposit_payment_keyboard(payment_url=deposit.payment_url, provider_payment_id=deposit.provider_payment_id)
        if deposit.payment_url
        else wallet_keyboard()
    )
    await send_section_message(
        callback_query.message,
        _("deposit created").format(
            amount=deposit.amount,
            payment_method=deposit.payment_method,
            provider_payment_id=deposit.provider_payment_id,
        ),
        section="profile",
        reply_markup=reply_markup,
        edit=True,
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{DEPOSIT_DETAILS_CALLBACK_PREFIX}:"))
async def deposit_details_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.from_user or not callback_query.message:
        await callback_query.answer(_("deposit unavailable"))
        return

    try:
        deposit_id = parse_deposit_details_callback(callback_query.data)
        deposit = await get_user_deposit(session=session, user_id=callback_query.from_user.id, deposit_id=deposit_id)
    except (ValueError, NoResultFound):
        await callback_query.answer(_("deposit unavailable"), show_alert=True)
        return

    text = _("deposit details").format(
        amount=deposit.amount,
        requested_amount=deposit.requested_amount,
        commission_amount=deposit.commission_amount,
        payment_method=deposit.payment_method,
        status=format_deposit_status(deposit.status),
        provider_payment_id=escape(deposit.provider_payment_id),
        created_at=deposit.created_at,
    )
    reply_markup = (
        deposit_payment_keyboard(payment_url=deposit.payment_url, provider_payment_id=deposit.provider_payment_id)
        if deposit.payment_url and deposit.status in {DepositStatus.PENDING.value, DepositStatus.WAITING.value}
        else deposit_history_keyboard([], page=0, has_next_page=False)
    )
    await send_section_message(callback_query.message, text, section="profile", reply_markup=reply_markup, edit=True)
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{CHECK_DEPOSIT_CALLBACK_PREFIX}:"))
async def check_deposit_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.from_user or not callback_query.message:
        await callback_query.answer(_("wallet unavailable"))
        return
    try:
        provider_payment_id = parse_check_deposit_callback(callback_query.data)
        if provider_payment_id.startswith(LOLZ_TRANSFER_COMMENT_PREFIX):
            if not settings.LOLZ_MARKET_ACCESS_TOKEN:
                await callback_query.answer(_("deposit check unavailable"), show_alert=True)
                return
            provider = LolzBalanceClient(
                access_token=settings.LOLZ_MARKET_ACCESS_TOKEN,
                base_url=settings.LOLZ_MARKET_BASE_URL,
            )
        else:
            if not settings.PLATEGA_MERCHANT_ID or not settings.PLATEGA_API_KEY:
                await callback_query.answer(_("deposit check unavailable"), show_alert=True)
                return
            provider = PlategaClient(
                merchant_id=settings.PLATEGA_MERCHANT_ID,
                api_key=settings.PLATEGA_API_KEY,
                base_url=settings.PLATEGA_BASE_URL,
            )
        update = await verify_deposit_with_provider(
            session=session,
            provider=provider,
            provider_payment_id=provider_payment_id,
            user_id=callback_query.from_user.id,
        )
    except (ValueError, NoResultFound, LolzPaymentApiError):
        await callback_query.answer(_("deposit unavailable"), show_alert=True)
        return

    await callback_query.answer(
        _("deposit status").format(status=format_deposit_status(update.status.value)),
        show_alert=True,
    )
    await send_wallet(callback_query.message, session=session, user_id=callback_query.from_user.id, edit=True)


async def send_wallet(message: types.Message, *, session: AsyncSession, user_id: int, edit: bool = False) -> None:
    user = await get_user(session, user_id)
    if user is None:
        text = _("wallet unavailable")
    else:
        text = _("wallet title").format(
            balance=user.balance,
            total_deposited=user.total_deposited,
            total_spent=user.total_spent,
            user_id=user.id,
            first_name=escape(user.first_name),
            username=escape(f"@{user.username}") if user.username else _("empty value"),
            language_code=user.language_code or _("empty value"),
            role=user.role,
        )

    reply_markup = wallet_keyboard()
    if edit:
        await send_section_message(message, text, section="profile", reply_markup=reply_markup, edit=True)
        return

    await send_section_message(message, text, section="profile", reply_markup=reply_markup)


async def send_deposit_history(
    message: types.Message,
    *,
    session: AsyncSession,
    user_id: int,
    page: int = 0,
) -> None:
    deposits_page = await list_user_deposits(session=session, user_id=user_id, page=page)
    text = _("deposit history title")
    if not deposits_page.deposits:
        text = _("deposit history empty")

    await send_section_message(
        message,
        text,
        section="profile",
        reply_markup=deposit_history_keyboard(
            deposits_page.deposits,
            page=page,
            has_next_page=deposits_page.has_next_page,
        ),
        edit=True,
    )


def format_deposit_status(status: str) -> str:
    if status == DepositStatus.PAID.value:
        return _("deposit status paid")
    if status in {DepositStatus.FAILED.value, DepositStatus.CANCELLED.value, DepositStatus.EXPIRED.value}:
        return _("deposit status failed")
    if status in {DepositStatus.PENDING.value, DepositStatus.WAITING.value}:
        return _("deposit status pending")
    return status
