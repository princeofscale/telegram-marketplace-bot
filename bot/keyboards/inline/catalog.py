from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.catalog.callbacks import CATALOG_CALLBACK, buy_callback, confirm_buy_callback, product_callback

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bot.database.models import CatalogProductModel


def catalog_keyboard(products: Sequence[tuple[CatalogProductModel, int]]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{product.title} - {product.display_price} ({available_count})",
                callback_data=product_callback(product.id),
            ),
        ]
        for product, available_count in products
    ]
    buttons.append([InlineKeyboardButton(text=_("back button"), callback_data="menu")])

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def product_keyboard(product: CatalogProductModel) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("buy button"), callback_data=confirm_buy_callback(product.id))],
        [InlineKeyboardButton(text=_("back button"), callback_data=CATALOG_CALLBACK)],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def purchase_confirmation_keyboard(product: CatalogProductModel) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("confirm purchase button"), callback_data=buy_callback(product.id))],
        [InlineKeyboardButton(text=_("back button"), callback_data=product_callback(product.id))],
        [InlineKeyboardButton(text=_("catalog button"), callback_data=CATALOG_CALLBACK)],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()
