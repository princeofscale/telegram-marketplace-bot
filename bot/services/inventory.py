from __future__ import annotations
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from bot.database.models import InventoryItemModel
from bot.modules.inventory.reservations import (
    decide_reservation_status,
    ensure_reserved,
    reserve_until,
)
from bot.modules.inventory.statuses import InventoryStatus

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


DEFAULT_RESERVATION_TTL_SECONDS = 30


class InventoryItemNotFoundError(ValueError):
    """Raised when an inventory item id does not exist."""


async def reserve_inventory_item(
    *,
    session: AsyncSession,
    item_id: UUID,
    ttl_seconds: int = DEFAULT_RESERVATION_TTL_SECONDS,
    commit: bool = True,
) -> InventoryItemModel:
    item = await get_locked_inventory_item(session=session, item_id=item_id)
    now = datetime.now(UTC).replace(tzinfo=None)
    decision = decide_reservation_status(
        current_status=InventoryStatus(item.status),
        reserved_until_value=item.reserved_until,
        now=now,
    )

    if decision.should_reserve:
        item.status = decision.status.value
        item.reserved_until = reserve_until(now, ttl_seconds)

    if commit:
        await session.commit()
    return item


async def release_inventory_reservation(
    *,
    session: AsyncSession,
    item_id: UUID,
    commit: bool = True,
) -> InventoryItemModel:
    item = await get_locked_inventory_item(session=session, item_id=item_id)
    ensure_reserved(InventoryStatus(item.status))
    item.status = InventoryStatus.AVAILABLE.value
    item.reserved_until = None
    if commit:
        await session.commit()
    return item


async def mark_inventory_sold(*, session: AsyncSession, item_id: UUID, commit: bool = True) -> InventoryItemModel:
    item = await get_locked_inventory_item(session=session, item_id=item_id)
    ensure_reserved(InventoryStatus(item.status))
    item.status = InventoryStatus.SOLD.value
    item.reserved_until = None
    if commit:
        await session.commit()
    return item


async def get_locked_inventory_item(*, session: AsyncSession, item_id: UUID) -> InventoryItemModel:
    result = await session.execute(select(InventoryItemModel).where(InventoryItemModel.id == item_id).with_for_update())
    item = result.scalar_one_or_none()
    if item is None:
        msg = "inventory_item_not_found"
        raise InventoryItemNotFoundError(msg)
    return item
