from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

from bot.services.users import sync_user_profile, user_exists

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject, User
    from sqlalchemy.ext.asyncio import AsyncSession


class UserSyncMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = getattr(event, "from_user", None)
        session: AsyncSession = data["session"]

        if user and await user_exists(session, user.id):
            await sync_user_profile(session, user)

        return await handler(event, data)
