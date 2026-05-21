from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.admins.callbacks import ADMIN_EXPORT_USERS_CALLBACK, ADMIN_STATS_CALLBACK


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("admin stats button"), callback_data=ADMIN_STATS_CALLBACK)],
        [InlineKeyboardButton(text=_("admin export users button"), callback_data=ADMIN_EXPORT_USERS_CALLBACK)],
        [InlineKeyboardButton(text=_("back button"), callback_data="menu")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()
