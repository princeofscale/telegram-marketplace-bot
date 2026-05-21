from decimal import Decimal
from uuid import uuid4

from bot.database.models import CatalogProductModel, InventoryItemModel, SourceProductModel
from bot.modules.catalog.callbacks import (
    BUY_CALLBACK_PREFIX,
    CONFIRM_BUY_CALLBACK_PREFIX,
    PRODUCT_CALLBACK_PREFIX,
    buy_callback,
    confirm_buy_callback,
    parse_product_callback,
    product_callback,
)
from bot.modules.catalog.pricing import MarkupPolicy, calculate_display_price
from bot.modules.inventory.statuses import InventoryStatus
from bot.services.catalog import build_catalog_product_from_source, list_available_catalog_products


def test_pricing_uses_product_category_global_priority() -> None:
    assert calculate_display_price(
        base_price=Decimal("100.00"),
        policy=MarkupPolicy(global_markup=Decimal(15), category_markup=Decimal(20), product_markup=Decimal(35)),
    ) == Decimal("135.00")
    assert calculate_display_price(
        base_price=Decimal("100.00"),
        policy=MarkupPolicy(global_markup=Decimal(15), category_markup=Decimal(20)),
    ) == Decimal("120.00")
    assert calculate_display_price(
        base_price=Decimal("100.00"),
        policy=MarkupPolicy(global_markup=Decimal(15)),
    ) == Decimal("115.00")


def test_inventory_statuses_match_purchase_flow() -> None:
    assert {status.value for status in InventoryStatus} == {
        "available",
        "reserved",
        "sold",
        "cancelled",
        "hidden",
    }


def test_catalog_inventory_models_have_expected_shape() -> None:
    source_columns = SourceProductModel.__table__.columns.keys()
    catalog_columns = CatalogProductModel.__table__.columns.keys()
    inventory_columns = InventoryItemModel.__table__.columns.keys()

    assert {"id", "source", "source_item_id", "raw_title", "raw_price", "category", "payload"} <= set(source_columns)
    assert {"id", "source_product_id", "title", "category", "display_price", "markup_percent"} <= set(catalog_columns)
    assert {"id", "catalog_product_id", "source", "encrypted_content", "status", "reserved_until"} <= set(
        inventory_columns,
    )


def test_build_catalog_product_persists_effective_markup_value() -> None:
    source = SourceProductModel(
        source="test",
        source_item_id="sku-1",
        raw_title="Account",
        raw_price=Decimal("100.00"),
        category="accounts",
    )

    product = build_catalog_product_from_source(source, global_markup=Decimal("10.00"))

    assert product.display_price == Decimal("110.00")
    assert product.markup_percent == Decimal("10.00")


def test_available_catalog_query_service_exists() -> None:
    assert callable(list_available_catalog_products)


def test_catalog_callbacks_roundtrip_product_ids() -> None:
    product_id = uuid4()

    assert parse_product_callback(product_callback(product_id), prefix=PRODUCT_CALLBACK_PREFIX) == product_id
    assert parse_product_callback(confirm_buy_callback(product_id), prefix=CONFIRM_BUY_CALLBACK_PREFIX) == product_id
    assert parse_product_callback(buy_callback(product_id), prefix=BUY_CALLBACK_PREFIX) == product_id
