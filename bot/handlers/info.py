from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.info import PRIVACY_POLICY_CALLBACK, info_keyboard, privacy_policy_keyboard
from bot.utils.messages import send_section_message

router = Router(name="info")


@router.callback_query(F.data == "info")
async def info_callback_handler(callback_query: types.CallbackQuery) -> None:
    if callback_query.message:
        await send_section_message(
            callback_query.message,
            _("about"),
            section="info",
            reply_markup=info_keyboard(),
            edit=True,
        )
    await callback_query.answer()


@router.callback_query(F.data == PRIVACY_POLICY_CALLBACK)
async def privacy_policy_callback_handler(callback_query: types.CallbackQuery) -> None:
    if callback_query.message:
        await send_section_message(
            callback_query.message,
            _("privacy policy"),
            section="info",
            reply_markup=privacy_policy_keyboard(),
            edit=True,
        )
    await callback_query.answer()
