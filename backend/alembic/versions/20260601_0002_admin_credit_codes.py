"""admin role and credit redemption codes

Revision ID: 20260601_0002
Revises: 20260601_0001
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0002"
down_revision: str | None = "20260601_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=30), nullable=False, server_default="user"))
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "credit_redemption_codes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("redeemed_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_credit_redemption_codes_code", "credit_redemption_codes", ["code"], unique=True)
    op.create_index("ix_credit_redemption_codes_status", "credit_redemption_codes", ["status"])
    op.create_index("ix_credit_redemption_codes_created_by_user_id", "credit_redemption_codes", ["created_by_user_id"])
    op.create_index("ix_credit_redemption_codes_redeemed_by_user_id", "credit_redemption_codes", ["redeemed_by_user_id"])

    op.execute(
        """
        UPDATE users
        SET role = 'admin', plan = 'admin'
        WHERE id = (SELECT id FROM (SELECT id FROM users ORDER BY created_at ASC LIMIT 1) AS first_user)
        """
    )


def downgrade() -> None:
    op.drop_table("credit_redemption_codes")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
