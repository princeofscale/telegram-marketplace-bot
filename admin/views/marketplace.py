# ruff: noqa: RUF012
from __future__ import annotations

from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup


class MarketplaceModelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    can_export = True
    details_modal = True
    export_types = ["csv", "xlsx", "json", "yaml"]


class DepositView(MarketplaceModelView):
    column_list = [
        "id",
        "user_id",
        "amount",
        "requested_amount",
        "commission_amount",
        "payment_method",
        "status",
        "provider_payment_id",
        "created_at",
        "paid_at",
    ]
    column_searchable_list = ["provider_payment_id", "user_id"]
    column_filters = ["status", "payment_method", "created_at", "paid_at"]
    column_default_sort = ("created_at", True)


class OrderView(MarketplaceModelView):
    column_list = [
        "id",
        "user_id",
        "product_id",
        "inventory_item_id",
        "sell_price",
        "profit",
        "status",
        "created_at",
        "completed_at",
    ]
    column_searchable_list = ["id", "user_id", "inventory_item_id"]
    column_filters = ["status", "source", "created_at", "completed_at"]
    column_default_sort = ("created_at", True)
    column_exclude_list = ["delivered_text"]
    column_details_exclude_list = ["delivered_text"]


class CatalogProductView(MarketplaceModelView):
    can_edit = True
    column_list = ["id", "title", "category", "display_price", "markup_percent", "is_hidden", "created_at"]
    column_searchable_list = ["title", "category"]
    column_filters = ["category", "is_hidden", "created_at"]
    column_editable_list = ["is_hidden", "display_price", "markup_percent"]
    column_default_sort = ("created_at", True)


class InventoryItemView(MarketplaceModelView):
    column_list = ["id", "catalog_product_id", "source", "status", "reserved_until", "created_at"]
    column_searchable_list = ["id", "catalog_product_id", "source"]
    column_filters = ["status", "source", "created_at", "reserved_until"]
    column_default_sort = ("created_at", True)
    column_exclude_list = ["encrypted_content"]
    column_details_exclude_list = ["encrypted_content"]


class SourceProductView(MarketplaceModelView):
    column_list = ["id", "source", "source_item_id", "raw_title", "raw_price", "category", "created_at"]
    column_searchable_list = ["source_item_id", "raw_title", "category"]
    column_filters = ["source", "category", "created_at"]
    column_default_sort = ("created_at", True)


class BalanceTransactionView(MarketplaceModelView):
    column_list = ["id", "user_id", "amount", "type", "balance_before", "balance_after", "comment", "created_at"]
    column_searchable_list = ["user_id", "comment"]
    column_filters = ["type", "created_at"]
    column_default_sort = ("created_at", True)


class AuditLogView(MarketplaceModelView):
    column_list = ["id", "actor_id", "action", "target_id", "created_at"]
    column_searchable_list = ["actor_id", "action", "target_id"]
    column_filters = ["action", "created_at"]
    column_default_sort = ("created_at", True)

    def _payload_formatter(self, _context: object, _model: object, name: str) -> Markup:
        value = getattr(_model, name)
        return Markup.escape(str(value))

    column_formatters = {"payload": _payload_formatter}


class SettingView(MarketplaceModelView):
    can_edit = True
    column_list = ["key", "value", "description", "updated_at"]
    column_searchable_list = ["key"]
    column_filters = ["updated_at"]
    column_editable_list = ["value", "description"]
