"""Add deposit payment URL.

Revision ID: 20260518_deposit_payment_url
Revises: 20260518_order_delivery_snapshot
Create Date: 2026-05-18 00:00:07.000000
"""

from __future__ import annotations
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260518_deposit_payment_url"
down_revision: Union[str, None] = "20260518_order_delivery_snapshot"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("deposits", sa.Column("payment_url", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("deposits", "payment_url")
