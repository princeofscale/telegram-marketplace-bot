"""catalog inventory

Revision ID: 20260518_catalog
Revises: 20260518_deposits
Create Date: 2026-05-18 00:00:04.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260518_catalog"
down_revision: Union[str, None] = "20260518_deposits"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "source_products",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("source_item_id", sa.String(length=128), nullable=False),
        sa.Column("raw_title", sa.String(length=512), nullable=False),
        sa.Column("raw_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("payload", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_products_category", "source_products", ["category"])
    op.create_index("ix_source_products_source", "source_products", ["source"])
    op.create_index("ix_source_products_source_item_id", "source_products", ["source_item_id"])

    op.create_table(
        "catalog_products",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_product_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("display_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("markup_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.ForeignKeyConstraint(["source_product_id"], ["source_products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_catalog_products_category", "catalog_products", ["category"])
    op.create_index("ix_catalog_products_source_product_id", "catalog_products", ["source_product_id"])

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("catalog_product_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("encrypted_content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reserved_until", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.ForeignKeyConstraint(["catalog_product_id"], ["catalog_products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inventory_items_catalog_product_id", "inventory_items", ["catalog_product_id"])
    op.create_index("ix_inventory_items_source", "inventory_items", ["source"])
    op.create_index("ix_inventory_items_status", "inventory_items", ["status"])


def downgrade() -> None:
    op.drop_index("ix_inventory_items_status", table_name="inventory_items")
    op.drop_index("ix_inventory_items_source", table_name="inventory_items")
    op.drop_index("ix_inventory_items_catalog_product_id", table_name="inventory_items")
    op.drop_table("inventory_items")
    op.drop_index("ix_catalog_products_source_product_id", table_name="catalog_products")
    op.drop_index("ix_catalog_products_category", table_name="catalog_products")
    op.drop_table("catalog_products")
    op.drop_index("ix_source_products_source_item_id", table_name="source_products")
    op.drop_index("ix_source_products_source", table_name="source_products")
    op.drop_index("ix_source_products_category", table_name="source_products")
    op.drop_table("source_products")
