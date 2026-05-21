"""settings

Revision ID: 20260518_settings
Revises: 20260518_audit_logs
Create Date: 2026-05-18 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260518_settings"
down_revision: Union[str, None] = "20260518_audit_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    op.execute(
        """
        INSERT INTO settings (key, value, description)
        VALUES
            ('global_markup', '"15.00"'::json, 'Default product markup percent'),
            ('captcha_enabled', 'true'::json, 'Require captcha before registration'),
            ('referrals_enabled', 'true'::json, 'Enable referral attribution'),
            ('min_deposit', '"100.00"'::json, 'Minimum deposit amount')
        """,
    )


def downgrade() -> None:
    op.drop_table("settings")
