"""Add order delivery snapshot timestamp.

Revision ID: 20260518_order_delivery_snapshot
Revises: 20260518_orders
Create Date: 2026-05-18 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260518_order_delivery_snapshot"
down_revision = "20260518_orders"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("delivered_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "delivered_at")
