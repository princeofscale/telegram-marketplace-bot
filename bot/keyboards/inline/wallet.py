from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.payments.callbacks import (
    DEPOSIT_HISTORY_CALLBACK,
    TOP_UP_CALLBACK,
    check_deposit_callback,
    deposit_callback,
    deposit_details_callback,
    deposit_history_page_callback,
    deposit_method_callback,
)
from bot.modules.payments.lolz import LOLZ_BALANCE_PAYMENT_METHOD, LOLZ_BALANCE_PAYMENT_TITLE
from bot.modules.payments.platega import PLATEGA_PAYMENT_METHODS

if TYPE_CHECKING:
    from bot.database.models import DepositModel

DEFAULT_DEPOSIT_AMOUNTS = (
    Decimal("50.00"),
    Decimal("100.00"),
    Decimal("200.00"),
    Decimal("500.00"),
    Decimal("1000.00"),
)


def wallet_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("top up button"), callback_data=TOP_UP_CALLBACK)],
        [InlineKeyboardButton(text=_("deposit history button"), callback_data=DEPOSIT_HISTORY_CALLBACK)],
        [InlineKeyboardButton(text=_("back button"), callback_data="menu")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def top_up_keyboard(amounts: tuple[Decimal, ...] = DEFAULT_DEPOSIT_AMOUNTS) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=_("deposit amount button").format(amount=amount),
                callback_data=deposit_callback(amount),
            ),
        ]
        for amount in amounts
    ]
    buttons.append([InlineKeyboardButton(text=_("back button"), callback_data="wallet")])

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(2, 2, 1, 1)
    return keyboard.as_markup()


def deposit_method_keyboard(
    amount: Decimal,
    *,
    include_platega: bool = True,
    include_lolz_balance: bool = False,
) -> InlineKeyboardMarkup:
    buttons = []
    if include_lolz_balance:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=LOLZ_BALANCE_PAYMENT_TITLE,
                    callback_data=deposit_method_callback(amount, LOLZ_BALANCE_PAYMENT_METHOD),
                ),
            ],
        )

    if include_platega:
        buttons.extend(
            [
                [
                    InlineKeyboardButton(
                        text=f"{policy.title} +{policy.commission_percent}%",
                        callback_data=deposit_method_callback(amount, policy.method.value),
                    ),
                ]
                for policy in PLATEGA_PAYMENT_METHODS.values()
            ],
        )

    if not buttons:
        buttons = [
            [
                InlineKeyboardButton(
                    text=_("manual payment method button"),
                    callback_data=deposit_method_callback(amount, "manual"),
                ),
            ],
        ]

    buttons.append([InlineKeyboardButton(text=_("back button"), callback_data="wallet")])

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def deposit_payment_keyboard(*, payment_url: str, provider_payment_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("pay button"), url=payment_url)],
        [
            InlineKeyboardButton(
                text=_("check payment button"),
                callback_data=check_deposit_callback(provider_payment_id),
            ),
        ],
        [InlineKeyboardButton(text=_("back button"), callback_data="wallet")],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def deposit_history_keyboard(
    deposits: list[DepositModel],
    *,
    page: int,
    has_next_page: bool,
) -> InlineKeyboardMarkup:
    status_text = {
        "paid": _("deposit status paid"),
        "failed": _("deposit status failed"),
        "cancelled": _("deposit status failed"),
        "expired": _("deposit status failed"),
        "pending": _("deposit status pending"),
        "waiting": _("deposit status pending"),
    }
    buttons = [
        [
            InlineKeyboardButton(
                text=_("deposit history item button").format(
                    amount=deposit.amount,
                    status=status_text.get(deposit.status, deposit.status),
                ),
                callback_data=deposit_details_callback(deposit.id),
            ),
        ]
        for deposit in deposits
    ]

    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(text=_("previous page button"), callback_data=deposit_history_page_callback(page - 1)),
        )
    if has_next_page:
        pagination_buttons.append(
            InlineKeyboardButton(text=_("next page button"), callback_data=deposit_history_page_callback(page + 1)),
        )
    if pagination_buttons:
        buttons.append(pagination_buttons)

    buttons.append([InlineKeyboardButton(text=_("back button"), callback_data="wallet")])

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()
