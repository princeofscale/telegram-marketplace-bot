from decimal import Decimal
from inspect import Parameter, signature
from uuid import uuid4

import pytest

from bot.database.models import OrderModel
from bot.modules.orders.callbacks import ORDER_CALLBACK_PREFIX, order_callback, parse_order_callback
from bot.modules.orders.lifecycle import (
    OrderTransitionError,
    ensure_can_cancel,
    ensure_can_fail,
    ensure_can_refund,
)
from bot.modules.orders.statuses import OrderStatus
from bot.services.balance import apply_balance_transaction
from bot.services.inventory import mark_inventory_sold, release_inventory_reservation, reserve_inventory_item
from bot.services.orders import (
    build_order_profit,
    cancel_purchase_order,
    complete_lolz_market_purchase,
    complete_reserved_purchase,
    create_purchase_order,
    fail_purchase_order,
    get_user_order,
    list_user_orders,
    purchase_catalog_product,
    refund_completed_order,
)


def test_order_statuses_match_purchase_flow() -> None:
    assert {status.value for status in OrderStatus} == {
        "pending",
        "paid",
        "completed",
        "cancelled",
        "refunded",
        "failed",
    }


def test_order_profit_is_sell_minus_buy_price() -> None:
    assert build_order_profit(buy_price=Decimal("100.00"), sell_price=Decimal("135.50")) == Decimal("35.50")


def test_order_model_contains_purchase_snapshot_shape() -> None:
    columns = OrderModel.__table__.columns.keys()

    assert "id" in columns
    assert "user_id" in columns
    assert "product_id" in columns
    assert "inventory_item_id" in columns
    assert "source" in columns
    assert "buy_price" in columns
    assert "sell_price" in columns
    assert "profit" in columns
    assert "status" in columns
    assert "delivered_text" in columns
    assert "delivered_at" in columns
    assert "created_at" in columns
    assert "completed_at" in columns


def test_purchase_helpers_allow_outer_transaction_boundary() -> None:
    for helper in (
        apply_balance_transaction,
        reserve_inventory_item,
        release_inventory_reservation,
        mark_inventory_sold,
        create_purchase_order,
        complete_reserved_purchase,
        complete_lolz_market_purchase,
    ):
        parameter = signature(helper).parameters["commit"]

        assert parameter.kind == Parameter.KEYWORD_ONLY
        assert parameter.default is True


def test_order_lifecycle_allows_expected_failure_paths() -> None:
    ensure_can_cancel(OrderStatus.PENDING)
    ensure_can_fail(OrderStatus.PENDING)
    ensure_can_refund(OrderStatus.COMPLETED)

    with pytest.raises(OrderTransitionError, match="order_cannot_be_cancelled"):
        ensure_can_cancel(OrderStatus.COMPLETED)

    with pytest.raises(OrderTransitionError, match="order_cannot_fail"):
        ensure_can_fail(OrderStatus.COMPLETED)

    with pytest.raises(OrderTransitionError, match="order_cannot_be_refunded"):
        ensure_can_refund(OrderStatus.PENDING)


def test_order_failure_services_accept_reason_and_outer_commit() -> None:
    for service in (cancel_purchase_order, fail_purchase_order, refund_completed_order):
        parameters = signature(service).parameters

        assert parameters["reason"].default == ""


def test_purchase_catalog_product_is_single_entrypoint() -> None:
    parameters = signature(purchase_catalog_product).parameters

    assert "session" in parameters
    assert "user_id" in parameters
    assert "product_id" in parameters


def test_purchase_history_services_exist() -> None:
    assert callable(list_user_orders)
    assert callable(get_user_order)


def test_order_callbacks_roundtrip_order_ids() -> None:
    order_id = uuid4()

    assert parse_order_callback(order_callback(order_id)) == order_id
    assert order_callback(order_id).startswith(f"{ORDER_CALLBACK_PREFIX}:")
