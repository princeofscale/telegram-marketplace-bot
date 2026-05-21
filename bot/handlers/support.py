from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.contacts import support_keyboard
from bot.utils.messages import send_section_message

router = Router(name="support")


@router.callback_query(F.data == "support")
async def support_callback_handler(callback_query: types.CallbackQuery) -> None:
    if callback_query.message:
        await send_section_message(
            callback_query.message,
            _("support text"),
            section="help",
            reply_markup=support_keyboard(),
            edit=True,
        )
    await callback_query.answer()
