from __future__ import annotations
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select

from bot.core.config import settings
from bot.database.models import CatalogProductModel, InventoryItemModel, OrderModel, SourceProductModel
from bot.modules.audit.events import AuditAction, AuditEvent
from bot.modules.balance.ledger import TransactionType
from bot.modules.inventory.statuses import InventoryStatus
from bot.modules.orders.lifecycle import ensure_can_cancel, ensure_can_fail, ensure_can_refund
from bot.modules.orders.statuses import OrderStatus
from bot.modules.providers.lolz_market import LOLZ_MARKET_SOURCE
from bot.modules.security.inventory_crypto import InventoryCipher
from bot.services.audit import add_audit_log
from bot.services.balance import BalanceTransactionRequest, apply_balance_transaction
from bot.services.delivery import build_delivery_snapshot
from bot.services.inventory import mark_inventory_sold, release_inventory_reservation, reserve_inventory_item
from bot.services.lolz_market import LolzMarketApiError, LolzMarketClient

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class ProductNotFoundError(ValueError):
    """Raised when a catalog product id does not exist."""


class NoInventoryAvailableError(ValueError):
    """Raised when a catalog product has no available inventory."""


class OrderNotFoundError(ValueError):
    """Raised when a user order does not exist."""


def build_order_profit(*, buy_price: Decimal, sell_price: Decimal) -> Decimal:
    return (sell_price - buy_price).quantize(Decimal("0.01"))


async def create_purchase_order(
    *,
    session: AsyncSession,
    user_id: int,
    product_id: UUID,
    commit: bool = True,
) -> OrderModel:
    product_result = await session.execute(select(CatalogProductModel).where(CatalogProductModel.id == product_id))
    product = product_result.scalar_one_or_none()
    if product is None:
        msg = "product_not_found"
        raise ProductNotFoundError(msg)

    item_result = await session.execute(
        select(InventoryItemModel)
        .where(
            InventoryItemModel.catalog_product_id == product_id,
            InventoryItemModel.status == "available",
        )
        .limit(1),
    )
    item = item_result.scalar_one_or_none()
    if item is None:
        msg = "no_inventory_available"
        raise NoInventoryAvailableError(msg)

    await reserve_inventory_item(session=session, item_id=item.id, commit=False)
    order = OrderModel(
        user_id=user_id,
        product_id=product.id,
        inventory_item_id=item.id,
        source=item.source,
        buy_price=Decimal("0.00"),
        sell_price=product.display_price,
        profit=build_order_profit(buy_price=Decimal("0.00"), sell_price=product.display_price),
        status=OrderStatus.PENDING.value,
    )
    session.add(order)
    await session.flush()
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.ORDER_CREATED,
            actor_id=user_id,
            target_id=str(order.id),
            payload={"product_id": str(product.id), "inventory_item_id": str(item.id)},
        ),
    )
    if commit:
        await session.commit()
    return order


async def complete_reserved_purchase(*, session: AsyncSession, order: OrderModel, commit: bool = True) -> OrderModel:
    if order.source == LOLZ_MARKET_SOURCE:
        return await complete_lolz_market_purchase(session=session, order=order, commit=commit)

    await apply_balance_transaction(
        session=session,
        request=BalanceTransactionRequest(
            user_id=order.user_id,
            amount=-order.sell_price,
            transaction_type=TransactionType.PURCHASE,
            comment=f"order:{order.id}",
        ),
        commit=False,
    )
    item = await mark_inventory_sold(session=session, item_id=order.inventory_item_id, commit=False)
    delivery = build_delivery_snapshot(encrypted_inventory_content=item.encrypted_content)
    order.status = OrderStatus.COMPLETED.value
    order.delivered_text = delivery.encrypted_text
    order.delivered_at = delivery.delivered_at
    order.completed_at = datetime.now(UTC).replace(tzinfo=None)
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.ORDER_COMPLETED,
            actor_id=order.user_id,
            target_id=str(order.id),
            payload={"sell_price": str(order.sell_price), "inventory_item_id": str(order.inventory_item_id)},
        ),
    )
    if commit:
        await session.commit()
    return order


async def complete_lolz_market_purchase(*, session: AsyncSession, order: OrderModel, commit: bool = True) -> OrderModel:
    if not settings.LOLZ_MARKET_ACCESS_TOKEN:
        msg = "lolz_market_access_token_required"
        raise LolzMarketApiError(msg)

    source_product = await get_order_source_product(session=session, order=order)
    item = await reserve_inventory_item(session=session, item_id=order.inventory_item_id, commit=False)

    await apply_balance_transaction(
        session=session,
        request=BalanceTransactionRequest(
            user_id=order.user_id,
            amount=-order.sell_price,
            transaction_type=TransactionType.PURCHASE,
            comment=f"order:{order.id}",
        ),
        commit=False,
    )

    client = LolzMarketClient(
        access_token=settings.LOLZ_MARKET_ACCESS_TOKEN,
        base_url=settings.LOLZ_MARKET_BASE_URL,
    )
    purchase = await client.reserve_check_confirm_buy(
        item_id=int(source_product.source_item_id),
        price=source_product.raw_price,
    )

    encrypted_delivery = InventoryCipher(settings.INVENTORY_ENCRYPTION_KEY).encrypt(purchase.raw_delivery)
    item.encrypted_content = encrypted_delivery
    item.status = InventoryStatus.SOLD.value
    item.reserved_until = None

    delivery = build_delivery_snapshot(encrypted_inventory_content=encrypted_delivery)
    order.buy_price = source_product.raw_price
    order.profit = build_order_profit(buy_price=order.buy_price, sell_price=order.sell_price)
    order.status = OrderStatus.COMPLETED.value
    order.delivered_text = delivery.encrypted_text
    order.delivered_at = delivery.delivered_at
    order.completed_at = datetime.now(UTC).replace(tzinfo=None)
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.ORDER_COMPLETED,
            actor_id=order.user_id,
            target_id=str(order.id),
            payload={
                "sell_price": str(order.sell_price),
                "buy_price": str(order.buy_price),
                "inventory_item_id": str(order.inventory_item_id),
                "provider": LOLZ_MARKET_SOURCE,
                "provider_item_id": source_product.source_item_id,
            },
        ),
    )
    if commit:
        await session.commit()
    return order


async def get_order_source_product(*, session: AsyncSession, order: OrderModel) -> SourceProductModel:
    result = await session.execute(
        select(SourceProductModel)
        .join(CatalogProductModel, CatalogProductModel.source_product_id == SourceProductModel.id)
        .where(CatalogProductModel.id == order.product_id),
    )
    source_product = result.scalar_one_or_none()
    if source_product is None:
        msg = "source_product_not_found"
        raise ProductNotFoundError(msg)
    return source_product


async def purchase_catalog_product(*, session: AsyncSession, user_id: int, product_id: UUID) -> OrderModel:
    order = await create_purchase_order(session=session, user_id=user_id, product_id=product_id, commit=False)
    await complete_reserved_purchase(session=session, order=order, commit=False)
    await session.commit()
    return order


async def cancel_purchase_order(*, session: AsyncSession, order: OrderModel, reason: str = "") -> OrderModel:
    ensure_can_cancel(OrderStatus(order.status))
    await release_inventory_reservation(session=session, item_id=order.inventory_item_id, commit=False)
    order.status = OrderStatus.CANCELLED.value
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.ORDER_CANCELLED,
            actor_id=order.user_id,
            target_id=str(order.id),
            payload={"reason": reason or None, "inventory_item_id": str(order.inventory_item_id)},
        ),
    )
    await session.commit()
    return order


async def fail_purchase_order(*, session: AsyncSession, order: OrderModel, reason: str = "") -> OrderModel:
    ensure_can_fail(OrderStatus(order.status))
    await release_inventory_reservation(session=session, item_id=order.inventory_item_id, commit=False)
    order.status = OrderStatus.FAILED.value
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.ORDER_FAILED,
            actor_id=order.user_id,
            target_id=str(order.id),
            payload={"reason": reason or None, "inventory_item_id": str(order.inventory_item_id)},
        ),
    )
    await session.commit()
    return order


async def refund_completed_order(*, session: AsyncSession, order: OrderModel, reason: str = "") -> OrderModel:
    ensure_can_refund(OrderStatus(order.status))
    await apply_balance_transaction(
        session=session,
        request=BalanceTransactionRequest(
            user_id=order.user_id,
            amount=order.sell_price,
            transaction_type=TransactionType.REFUND,
            comment=f"refund:{order.id}",
        ),
        commit=False,
    )
    order.status = OrderStatus.REFUNDED.value
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.ORDER_REFUNDED,
            actor_id=order.user_id,
            target_id=str(order.id),
            payload={"reason": reason or None, "sell_price": str(order.sell_price)},
        ),
    )
    await session.commit()
    return order


async def list_user_orders(*, session: AsyncSession, user_id: int, limit: int = 10) -> list[OrderModel]:
    result = await session.execute(
        select(OrderModel).where(OrderModel.user_id == user_id).order_by(OrderModel.created_at.desc()).limit(limit),
    )
    return list(result.scalars().all())


async def get_user_order(*, session: AsyncSession, user_id: int, order_id: UUID) -> OrderModel:
    result = await session.execute(select(OrderModel).where(OrderModel.id == order_id, OrderModel.user_id == user_id))
    order = result.scalar_one_or_none()
    if order is None:
        msg = "order_not_found"
        raise OrderNotFoundError(msg)
    return order
