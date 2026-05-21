from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.captcha.challenge import CaptchaChallenge


def captcha_keyboard(challenge: CaptchaChallenge | None = None) -> InlineKeyboardMarkup:
    challenge = challenge or CaptchaChallenge.inline_button()
    keyboard = InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(
                    text=_("captcha pass button"),
                    callback_data=challenge.pass_callback_data,
                    style=challenge.style,
                ),
            ],
        ],
    )
    return keyboard.as_markup()
