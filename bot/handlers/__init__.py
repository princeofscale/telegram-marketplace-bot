from aiogram import Router

from . import admin, captcha, catalog, export_users, info, menu, purchases, settings, start, support, wallet


def get_handlers_router() -> Router:
    router = Router()
    router.include_router(captcha.router)
    router.include_router(start.router)
    router.include_router(catalog.router)
    router.include_router(purchases.router)
    router.include_router(wallet.router)
    router.include_router(settings.router)
    router.include_router(admin.router)
    router.include_router(info.router)
    router.include_router(support.router)
    router.include_router(menu.router)
    router.include_router(export_users.router)

    return router
