from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from .auth import AuthMiddleware
from .database import DatabaseMiddleware
from .i18n import ACLMiddleware
from .logging import LoggingMiddleware
from .throttling import ThrottlingMiddleware
from .user_sync import UserSyncMiddleware
from bot.core.loader import i18n as _i18n


def register_middlewares(dp: Dispatcher) -> None:
    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(LoggingMiddleware())

    dp.update.outer_middleware(DatabaseMiddleware())

    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(UserSyncMiddleware())
    dp.callback_query.middleware(UserSyncMiddleware())

    ACLMiddleware(i18n=_i18n).setup(dp)

    dp.callback_query.middleware(CallbackAnswerMiddleware())
