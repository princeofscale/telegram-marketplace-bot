from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.profile.callbacks import LANGUAGE_SETTINGS_CALLBACK, SETTINGS_CALLBACK, language_callback

AVAILABLE_LANGUAGES = ("ru", "en", "uk")


def settings_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("language settings button"), callback_data=LANGUAGE_SETTINGS_CALLBACK)],
        [InlineKeyboardButton(text=_("back button"), callback_data="menu")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def language_settings_keyboard(current_language: str | None = None) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=language_button_text(language_code, current_language=current_language),
                callback_data=language_callback(language_code),
            ),
        ]
        for language_code in AVAILABLE_LANGUAGES
    ]
    buttons.append([InlineKeyboardButton(text=_("back button"), callback_data=SETTINGS_CALLBACK)])

    keyboard = InlineKeyboardBuilder(markup=buttons)
    keyboard.adjust(1)
    return keyboard.as_markup()


def language_button_text(language_code: str, *, current_language: str | None) -> str:
    labels = {
        "ru": _("language ru button"),
        "en": _("language en button"),
        "uk": _("language uk button"),
    }
    label = labels.get(language_code, language_code)
    if language_code == current_language:
        return _("selected language button").format(language=label)
    return label
