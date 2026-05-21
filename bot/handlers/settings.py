from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.settings import AVAILABLE_LANGUAGES, language_settings_keyboard, settings_keyboard
from bot.modules.profile.callbacks import (
    LANGUAGE_CALLBACK_PREFIX,
    LANGUAGE_SETTINGS_CALLBACK,
    SETTINGS_CALLBACK,
    parse_language_callback,
)
from bot.services.users import get_language_code, set_language_code
from bot.utils.messages import send_section_message

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router(name="settings")


@router.callback_query(F.data == SETTINGS_CALLBACK)
async def settings_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if callback_query.message and callback_query.from_user:
        await send_settings(callback_query.message, session=session, user_id=callback_query.from_user.id, edit=True)
    await callback_query.answer()


@router.callback_query(F.data == LANGUAGE_SETTINGS_CALLBACK)
async def language_settings_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if callback_query.message and callback_query.from_user:
        language_code = await get_language_code(session=session, user_id=callback_query.from_user.id)
        await send_section_message(
            callback_query.message,
            _("language settings title").format(language_code=language_code or _("empty value")),
            section="settings",
            reply_markup=language_settings_keyboard(language_code),
            edit=True,
        )
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{LANGUAGE_CALLBACK_PREFIX}:"))
async def language_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.from_user or not callback_query.message:
        await callback_query.answer(_("settings unavailable"))
        return

    try:
        language_code = parse_language_callback(callback_query.data)
    except ValueError:
        await callback_query.answer(_("settings unavailable"), show_alert=True)
        return

    if language_code not in AVAILABLE_LANGUAGES:
        await callback_query.answer(_("settings unavailable"), show_alert=True)
        return

    await set_language_code(session=session, user_id=callback_query.from_user.id, language_code=language_code)
    await send_section_message(
        callback_query.message,
        _("language changed").format(language_code=language_code),
        section="settings",
        reply_markup=language_settings_keyboard(language_code),
        edit=True,
    )
    await callback_query.answer()


async def send_settings(
    message: types.Message,
    *,
    session: AsyncSession,
    user_id: int,
    edit: bool = False,
) -> None:
    language_code = await get_language_code(session=session, user_id=user_id)
    text = _("settings title").format(language_code=language_code or _("empty value"))
    reply_markup = settings_keyboard()

    if edit:
        await send_section_message(message, text, section="settings", reply_markup=reply_markup, edit=True)
        return

    await send_section_message(message, text, section="settings", reply_markup=reply_markup)
