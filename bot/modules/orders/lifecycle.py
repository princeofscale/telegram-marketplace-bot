from __future__ import annotations

from bot.modules.orders.statuses import OrderStatus


class OrderTransitionError(ValueError):
    """Raised when an order cannot move to the requested status."""


def ensure_can_cancel(current_status: OrderStatus) -> None:
    if current_status != OrderStatus.PENDING:
        msg = "order_cannot_be_cancelled"
        raise OrderTransitionError(msg)


def ensure_can_fail(current_status: OrderStatus) -> None:
    if current_status != OrderStatus.PENDING:
        msg = "order_cannot_fail"
        raise OrderTransitionError(msg)


def ensure_can_refund(current_status: OrderStatus) -> None:
    if current_status != OrderStatus.COMPLETED:
        msg = "order_cannot_be_refunded"
        raise OrderTransitionError(msg)
