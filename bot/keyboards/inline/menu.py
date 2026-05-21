from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.admins.callbacks import ADMIN_PANEL_CALLBACK
from bot.modules.catalog.callbacks import CATALOG_CALLBACK
from bot.modules.orders.callbacks import PURCHASES_CALLBACK
from bot.modules.payments.callbacks import WALLET_CALLBACK
from bot.modules.profile.callbacks import SETTINGS_CALLBACK


def main_keyboard(*, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Use in main menu."""
    buttons = [
        [InlineKeyboardButton(text=_("catalog button"), callback_data=CATALOG_CALLBACK, style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text=_("wallet button"), callback_data=WALLET_CALLBACK)],
        [InlineKeyboardButton(text=_("purchases button"), callback_data=PURCHASES_CALLBACK)],
        [InlineKeyboardButton(text=_("settings button"), callback_data=SETTINGS_CALLBACK)],
        [InlineKeyboardButton(text=_("info button"), callback_data="info")],
        [InlineKeyboardButton(text=_("support button"), callback_data="support")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text=_("admin panel button"), callback_data=ADMIN_PANEL_CALLBACK)])

    keyboard = InlineKeyboardBuilder(markup=buttons)

    keyboard.adjust(1, 1, 1, 2, 1)

    return keyboard.as_markup()
