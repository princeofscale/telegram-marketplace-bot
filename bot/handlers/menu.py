from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.menu import main_keyboard
from bot.services.users import is_admin
from bot.utils.messages import send_section_message

router = Router(name="menu")


async def send_main_menu(
    message: types.Message,
    *,
    session: AsyncSession,
    user_id: int | None = None,
    edit: bool = False,
) -> None:
    user_id = user_id or (message.from_user.id if message.from_user else None)
    admin = bool(user_id and await is_admin(session=session, user_id=user_id))
    text = _("title main keyboard")
    reply_markup = main_keyboard(is_admin=admin)
    await send_section_message(message, text, section="menu", reply_markup=reply_markup, edit=edit)


@router.callback_query(F.data == "menu")
async def menu_callback_handler(callback_query: types.CallbackQuery, session) -> None:  # noqa: ANN001
    if callback_query.message:
        user_id = callback_query.from_user.id if callback_query.from_user else None
        await send_main_menu(callback_query.message, session=session, user_id=user_id, edit=True)
    await callback_query.answer()
