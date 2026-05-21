from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from loguru import logger

from bot.keyboards.inline.captcha import captcha_keyboard
from bot.modules.captcha.challenge import CaptchaChallenge
from bot.services.registration import create_pending_registration
from bot.services.users import user_exists
from bot.utils.command import find_command_argument

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject
    from sqlalchemy.ext.asyncio import AsyncSession


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        session: AsyncSession = data["session"]
        message: Message = event
        user = message.from_user

        if not user:
            return await handler(event, data)

        if await user_exists(session, user.id):
            return await handler(event, data)

        if not message.text or not message.text.startswith("/start"):
            await message.answer(_("registration required"))
            return None

        referrer = find_command_argument(message.text)
        await create_pending_registration(user_id=user.id, referrer=referrer)

        logger.info(f"new captcha registration pending | user_id: {user.id}")

        await message.answer(_("captcha prompt"), reply_markup=captcha_keyboard(CaptchaChallenge.inline_button()))
        return None
