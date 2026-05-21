from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

PRIVACY_POLICY_CALLBACK = "privacy_policy"


def info_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder(
        markup=[
            [InlineKeyboardButton(text=_("privacy policy button"), callback_data=PRIVACY_POLICY_CALLBACK)],
            [InlineKeyboardButton(text=_("back button"), callback_data="menu")],
        ],
    )
    return keyboard.as_markup()


def privacy_policy_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder(
        markup=[
            [InlineKeyboardButton(text=_("back button"), callback_data="info")],
            [InlineKeyboardButton(text=_("main menu button"), callback_data="menu")],
        ],
    )
    return keyboard.as_markup()
