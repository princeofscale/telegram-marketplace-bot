"""Add deposit commission amounts.

Revision ID: 20260518_deposit_commissions
Revises: 20260518_deposit_payment_url
Create Date: 2026-05-18 00:00:08.000000
"""

from __future__ import annotations
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260518_deposit_commissions"
down_revision: Union[str, None] = "20260518_deposit_payment_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "deposits",
        sa.Column("requested_amount", sa.Numeric(12, 2), server_default="0", nullable=False),
    )
    op.add_column(
        "deposits",
        sa.Column("commission_amount", sa.Numeric(12, 2), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("deposits", "commission_amount")
    op.drop_column("deposits", "requested_amount")
