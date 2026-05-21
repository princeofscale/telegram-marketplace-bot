from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta

from bot.modules.inventory.statuses import InventoryStatus


class InventoryTransitionError(ValueError):
    """Raised when an inventory item cannot move to the requested status."""


@dataclass(frozen=True)
class ReservationDecision:
    status: InventoryStatus
    should_reserve: bool


def reserve_until(now: datetime, ttl_seconds: int) -> datetime:
    return now + timedelta(seconds=ttl_seconds)


def decide_reservation_status(
    *,
    current_status: InventoryStatus,
    reserved_until_value: datetime | None,
    now: datetime,
) -> ReservationDecision:
    if current_status == InventoryStatus.AVAILABLE:
        return ReservationDecision(status=InventoryStatus.RESERVED, should_reserve=True)

    if current_status == InventoryStatus.RESERVED and reserved_until_value is not None and reserved_until_value <= now:
        return ReservationDecision(status=InventoryStatus.RESERVED, should_reserve=True)

    msg = "item_not_available"
    raise InventoryTransitionError(msg)


def ensure_reserved(current_status: InventoryStatus) -> None:
    if current_status != InventoryStatus.RESERVED:
        msg = "item_not_reserved"
        raise InventoryTransitionError(msg)
