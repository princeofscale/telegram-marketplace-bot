from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _

from bot.core.config import settings
from bot.keyboards.inline.purchases import purchase_details_keyboard, purchases_keyboard
from bot.modules.orders.callbacks import ORDER_CALLBACK_PREFIX, PURCHASES_CALLBACK, parse_order_callback
from bot.modules.security.inventory_crypto import InventoryCipher
from bot.services.delivery import decrypt_delivery_snapshot
from bot.services.orders import OrderNotFoundError, get_user_order, list_user_orders
from bot.utils.messages import replace_message_text, send_section_message

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router(name="purchases")


@router.callback_query(F.data == PURCHASES_CALLBACK)
async def purchases_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if callback_query.message and callback_query.from_user:
        await send_purchases(callback_query.message, session=session, user_id=callback_query.from_user.id, edit=True)
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{ORDER_CALLBACK_PREFIX}:"))
async def order_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.message or not callback_query.from_user:
        await callback_query.answer(_("purchase unavailable"))
        return

    try:
        order_id = parse_order_callback(callback_query.data)
        order = await get_user_order(session=session, user_id=callback_query.from_user.id, order_id=order_id)
    except (OrderNotFoundError, ValueError):
        await callback_query.answer(_("purchase unavailable"), show_alert=True)
        return

    delivery = ""
    if order.delivered_text:
        delivery = decrypt_delivery_snapshot(
            encrypted_text=order.delivered_text,
            cipher=InventoryCipher(settings.INVENTORY_ENCRYPTION_KEY),
        )

    await replace_message_text(
        callback_query.message,
        _("purchase details").format(
            order_id=order.id,
            status=order.status,
            price=order.sell_price,
            delivery=delivery,
        ),
        reply_markup=purchase_details_keyboard(),
    )
    await callback_query.answer()


async def send_purchases(message: types.Message, *, session: AsyncSession, user_id: int, edit: bool = False) -> None:
    orders = await list_user_orders(session=session, user_id=user_id)
    text = _("purchases empty") if not orders else _("purchases title")
    reply_markup = purchases_keyboard(orders)

    if edit:
        await send_section_message(message, text, section="other", reply_markup=reply_markup, edit=True)
        return

    await send_section_message(message, text, section="other", reply_markup=reply_markup)
