from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.orders.callbacks import PURCHASES_CALLBACK, order_callback

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bot.database.models import OrderModel


def purchases_keyboard(orders: Sequence[OrderModel]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{order.created_at:%Y-%m-%d} - {order.status} - {order.sell_price}",
                callback_data=order_callback(order.id),
            ),
        ]
        for order in orders
    ]
    buttons.append([InlineKeyboardButton(text=_("back button"), callback_data="menu")])

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def purchase_details_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("back button"), callback_data=PURCHASES_CALLBACK)],
    ]
    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()
