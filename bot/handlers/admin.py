from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _

from bot.keyboards.inline.admin import admin_panel_keyboard
from bot.modules.admins.callbacks import ADMIN_EXPORT_USERS_CALLBACK, ADMIN_PANEL_CALLBACK, ADMIN_STATS_CALLBACK
from bot.services.admin import get_admin_stats
from bot.services.users import get_all_users, get_user_count, is_admin
from bot.utils.messages import send_section_message
from bot.utils.users_export import convert_users_to_csv

if TYPE_CHECKING:
    from aiogram.types import BufferedInputFile
    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.models import UserModel


router = Router(name="admin")


@router.callback_query(F.data == ADMIN_PANEL_CALLBACK)
async def admin_panel_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.from_user or not await is_admin(session=session, user_id=callback_query.from_user.id):
        await callback_query.answer(_("admin access denied"), show_alert=True)
        return

    if callback_query.message:
        await send_section_message(
            callback_query.message,
            _("admin panel title"),
            section="other",
            reply_markup=admin_panel_keyboard(),
            edit=True,
        )
    await callback_query.answer()


@router.callback_query(F.data == ADMIN_STATS_CALLBACK)
async def admin_stats_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.from_user or not await is_admin(session=session, user_id=callback_query.from_user.id):
        await callback_query.answer(_("admin access denied"), show_alert=True)
        return

    stats = await get_admin_stats(session)
    text = _("admin stats text").format(
        users_count=stats.users_count,
        admins_count=stats.admins_count,
        deposits_count=stats.deposits_count,
        paid_deposits_count=stats.paid_deposits_count,
        paid_deposits_amount=stats.paid_deposits_amount,
        orders_count=stats.orders_count,
        catalog_products_count=stats.catalog_products_count,
        inventory_items_count=stats.inventory_items_count,
    )
    if callback_query.message:
        await send_section_message(
            callback_query.message,
            text,
            section="other",
            reply_markup=admin_panel_keyboard(),
            edit=True,
        )
    await callback_query.answer()


@router.callback_query(F.data == ADMIN_EXPORT_USERS_CALLBACK)
async def admin_export_users_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.from_user or not await is_admin(session=session, user_id=callback_query.from_user.id):
        await callback_query.answer(_("admin access denied"), show_alert=True)
        return

    all_users: list[UserModel] = await get_all_users(session)
    document: BufferedInputFile = await convert_users_to_csv(all_users)
    count: int = await get_user_count(session)

    if callback_query.message:
        await callback_query.message.answer_document(
            document=document,
            caption=_("user counter: <b>{count}</b>").format(count=count),
        )
    await callback_query.answer(_("admin export started"))
