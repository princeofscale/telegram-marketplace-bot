from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.i18n import gettext as _
from loguru import logger

from bot.handlers.menu import send_main_menu
from bot.modules.captcha.challenge import CAPTCHA_PASS_CALLBACK
from bot.services.registration import pop_pending_registration
from bot.services.users import add_user, user_exists

router = Router(name="captcha")


@router.callback_query(F.data == CAPTCHA_PASS_CALLBACK)
async def captcha_pass_handler(callback_query: types.CallbackQuery, bot: Bot, session) -> None:  # noqa: ANN001
    user = callback_query.from_user
    if callback_query.message:
        try:
            await callback_query.message.delete()
        except TelegramAPIError as exc:
            logger.warning(f"failed to delete captcha message | user_id: {user.id} | error: {exc}")

    if await user_exists(session, user.id):
        if callback_query.message:
            await send_main_menu(callback_query.message, session=session, user_id=user.id)
        return

    pending_registration = await pop_pending_registration(user.id)
    if pending_registration is None:
        if callback_query.message:
            await callback_query.message.answer(_("registration required"))
        return

    invited_by = await add_user(session=session, user=user, referrer=pending_registration.referrer)
    if invited_by is not None:
        try:
            await bot.send_message(
                invited_by,
                _("new referral notification").format(user_id=user.id, first_name=user.first_name),
            )
        except TelegramAPIError as exc:
            logger.warning(f"failed to notify inviter | inviter_id: {invited_by} | error: {exc}")

    if callback_query.message:
        await send_main_menu(callback_query.message, session=session, user_id=user.id)
