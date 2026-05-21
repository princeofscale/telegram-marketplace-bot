from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.handlers.menu import send_main_menu
from bot.services.analytics import analytics

router = Router(name="start")


@router.message(CommandStart())
@analytics.track_event("Sign Up")
async def start_handler(message: types.Message, session) -> None:  # noqa: ANN001
    """Welcome message."""
    user_id = message.from_user.id if message.from_user else None
    await send_main_menu(message, session=session, user_id=user_id)
