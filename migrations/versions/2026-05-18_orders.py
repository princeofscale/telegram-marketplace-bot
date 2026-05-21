"""orders

Revision ID: 20260518_orders
Revises: 20260518_catalog
Create Date: 2026-05-18 00:00:05.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260518_orders"
down_revision: Union[str, None] = "20260518_catalog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("inventory_item_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("buy_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("sell_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("profit", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("delivered_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_inventory_item_id", "orders", ["inventory_item_id"])
    op.create_index("ix_orders_product_id", "orders", ["product_id"])
    op.create_index("ix_orders_source", "orders", ["source"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_user_id", "orders", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_source", table_name="orders")
    op.drop_index("ix_orders_product_id", table_name="orders")
    op.drop_index("ix_orders_inventory_item_id", table_name="orders")
    op.drop_table("orders")
