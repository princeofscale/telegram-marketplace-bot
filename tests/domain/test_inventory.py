from datetime import UTC, datetime, timedelta

import pytest

from bot.modules.inventory.reservations import (
    InventoryTransitionError,
    ReservationDecision,
    decide_reservation_status,
    ensure_reserved,
    reserve_until,
)
from bot.modules.inventory.statuses import InventoryStatus


def test_reserve_until_uses_ttl_seconds() -> None:
    now = datetime(2026, 5, 18, tzinfo=UTC)

    assert reserve_until(now, ttl_seconds=30) == now + timedelta(seconds=30)


def test_available_item_can_be_reserved() -> None:
    decision = decide_reservation_status(
        current_status=InventoryStatus.AVAILABLE,
        reserved_until_value=None,
        now=datetime(2026, 5, 18, tzinfo=UTC),
    )

    assert decision == ReservationDecision(status=InventoryStatus.RESERVED, should_reserve=True)


def test_expired_reserved_item_can_be_re_reserved() -> None:
    now = datetime(2026, 5, 18, tzinfo=UTC)
    decision = decide_reservation_status(
        current_status=InventoryStatus.RESERVED,
        reserved_until_value=now - timedelta(seconds=1),
        now=now,
    )

    assert decision == ReservationDecision(status=InventoryStatus.RESERVED, should_reserve=True)


def test_active_reserved_item_cannot_be_reserved_again() -> None:
    now = datetime(2026, 5, 18, tzinfo=UTC)

    with pytest.raises(InventoryTransitionError, match="item_not_available"):
        decide_reservation_status(
            current_status=InventoryStatus.RESERVED,
            reserved_until_value=now + timedelta(seconds=30),
            now=now,
        )


def test_reserved_guard_rejects_non_reserved_statuses() -> None:
    ensure_reserved(InventoryStatus.RESERVED)

    with pytest.raises(InventoryTransitionError, match="item_not_reserved"):
        ensure_reserved(InventoryStatus.AVAILABLE)
