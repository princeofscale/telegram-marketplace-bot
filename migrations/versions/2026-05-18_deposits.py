"""deposits

Revision ID: 20260518_deposits
Revises: 20260518_settings
Create Date: 2026-05-18 00:00:03.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260518_deposits"
down_revision: Union[str, None] = "20260518_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "deposits",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=64), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_payment_id"),
    )
    op.create_index("ix_deposits_provider_payment_id", "deposits", ["provider_payment_id"])
    op.create_index("ix_deposits_status", "deposits", ["status"])
    op.create_index("ix_deposits_user_id", "deposits", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_deposits_user_id", table_name="deposits")
    op.drop_index("ix_deposits_status", table_name="deposits")
    op.drop_index("ix_deposits_provider_payment_id", table_name="deposits")
    op.drop_table("deposits")
