from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.utils.i18n import gettext as _

from bot.core.config import settings
from bot.keyboards.inline.catalog import catalog_keyboard, product_keyboard, purchase_confirmation_keyboard
from bot.modules.balance.ledger import InsufficientFundsError
from bot.modules.catalog.callbacks import (
    BUY_CALLBACK_PREFIX,
    CATALOG_CALLBACK,
    CONFIRM_BUY_CALLBACK_PREFIX,
    PRODUCT_CALLBACK_PREFIX,
    parse_product_callback,
)
from bot.modules.security.inventory_crypto import InventoryCipher
from bot.services.catalog import get_visible_catalog_product, list_available_catalog_products
from bot.services.delivery import decrypt_delivery_snapshot
from bot.services.orders import NoInventoryAvailableError, ProductNotFoundError, purchase_catalog_product
from bot.utils.messages import replace_message_text, send_section_message

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router(name="catalog")


@router.callback_query(F.data.in_({CATALOG_CALLBACK, "premium"}))
async def catalog_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if callback_query.message:
        await send_catalog(callback_query.message, session=session, edit=True)
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{PRODUCT_CALLBACK_PREFIX}:"))
async def product_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.message:
        await callback_query.answer(_("catalog unavailable"))
        return

    try:
        product_id = parse_product_callback(callback_query.data, prefix=PRODUCT_CALLBACK_PREFIX)
    except ValueError:
        await callback_query.answer(_("catalog unavailable"))
        return

    product = await get_visible_catalog_product(session=session, product_id=product_id)
    if product is None:
        await callback_query.answer(_("product unavailable"), show_alert=True)
        return

    text = _(
        "product details",
    ).format(title=product.title, category=product.category, price=product.display_price)
    await send_section_message(
        callback_query.message,
        text,
        section="catalog",
        reply_markup=product_keyboard(product),
        edit=True,
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{CONFIRM_BUY_CALLBACK_PREFIX}:"))
async def confirm_buy_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.message:
        await callback_query.answer(_("catalog unavailable"))
        return

    try:
        product_id = parse_product_callback(callback_query.data, prefix=CONFIRM_BUY_CALLBACK_PREFIX)
    except ValueError:
        await callback_query.answer(_("catalog unavailable"))
        return

    product = await get_visible_catalog_product(session=session, product_id=product_id)
    if product is None:
        await callback_query.answer(_("product unavailable"), show_alert=True)
        return

    text = _("purchase confirmation").format(
        title=product.title,
        category=product.category,
        price=product.display_price,
    )
    await send_section_message(
        callback_query.message,
        text,
        section="catalog",
        reply_markup=purchase_confirmation_keyboard(product),
        edit=True,
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith(f"{BUY_CALLBACK_PREFIX}:"))
async def buy_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    if not callback_query.data or not callback_query.from_user or not callback_query.message:
        await callback_query.answer(_("catalog unavailable"))
        return

    try:
        product_id = parse_product_callback(callback_query.data, prefix=BUY_CALLBACK_PREFIX)
        order = await purchase_catalog_product(
            session=session,
            user_id=callback_query.from_user.id,
            product_id=product_id,
        )
    except InsufficientFundsError:
        await callback_query.answer(_("insufficient funds"), show_alert=True)
        return
    except (NoInventoryAvailableError, ProductNotFoundError, ValueError):
        await callback_query.answer(_("product unavailable"), show_alert=True)
        return

    delivery_text = ""
    if order.delivered_text:
        delivery_text = decrypt_delivery_snapshot(
            encrypted_text=order.delivered_text,
            cipher=InventoryCipher(settings.INVENTORY_ENCRYPTION_KEY),
        )

    await replace_message_text(
        callback_query.message,
        _("purchase completed").format(order_id=order.id, price=order.sell_price, delivery=delivery_text),
    )
    await callback_query.answer()


async def send_catalog(message: types.Message, *, session: AsyncSession, edit: bool = False) -> None:
    products = await list_available_catalog_products(session=session)
    text = _("catalog empty") if not products else _("catalog title")
    reply_markup = catalog_keyboard(products)

    if edit:
        await send_section_message(message, text, section="catalog", reply_markup=reply_markup, edit=True)
        return

    await send_section_message(message, text, section="catalog", reply_markup=reply_markup)
