"""marketplace foundation

Revision ID: 20260518_marketplace
Revises: e4b7e8c165c1
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260518_marketplace"
down_revision: Union[str, None] = "e4b7e8c165c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=16), server_default="user", nullable=False))
    op.add_column("users", sa.Column("invited_by", sa.BigInteger(), nullable=True))
    op.add_column("users", sa.Column("referrals_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("users", sa.Column("referral_earnings", sa.Numeric(12, 2), server_default="0", nullable=False))
    op.add_column("users", sa.Column("balance", sa.Numeric(12, 2), server_default="0", nullable=False))
    op.add_column("users", sa.Column("total_deposited", sa.Numeric(12, 2), server_default="0", nullable=False))
    op.add_column("users", sa.Column("total_spent", sa.Numeric(12, 2), server_default="0", nullable=False))
    op.add_column("users", sa.Column("banned_reason", sa.Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column("registered_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    )
    op.add_column("users", sa.Column("last_activity_at", sa.DateTime(), nullable=True))
    op.add_column(
        "users",
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    )
    op.add_column("users", sa.Column("is_blocked", sa.Boolean(), server_default="false", nullable=False))
    op.create_index("ix_users_invited_by", "users", ["invited_by"])

    op.create_table(
        "user_balance_transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("balance_before", sa.Numeric(12, 2), nullable=False),
        sa.Column("balance_after", sa.Numeric(12, 2), nullable=False),
        sa.Column("comment", sa.Text(), server_default="", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_balance_transactions_user_id", "user_balance_transactions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_balance_transactions_user_id", table_name="user_balance_transactions")
    op.drop_table("user_balance_transactions")
    op.drop_index("ix_users_invited_by", table_name="users")
    op.drop_column("users", "is_blocked")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "last_activity_at")
    op.drop_column("users", "registered_at")
    op.drop_column("users", "banned_reason")
    op.drop_column("users", "total_spent")
    op.drop_column("users", "total_deposited")
    op.drop_column("users", "balance")
    op.drop_column("users", "referral_earnings")
    op.drop_column("users", "referrals_count")
    op.drop_column("users", "invited_by")
    op.drop_column("users", "role")
