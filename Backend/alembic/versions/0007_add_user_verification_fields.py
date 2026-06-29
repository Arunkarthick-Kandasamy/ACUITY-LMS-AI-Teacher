"""Add user verification fields and email_verification_tokens table.

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-28 13:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("date_of_birth", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("country", sa.String(100), nullable=True))
    op.add_column(
        "users",
        sa.Column("preferred_language", sa.String(10), server_default="en", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_email_verification_tokens_user_id"),
        "email_verification_tokens",
        ["user_id"],
    )
    op.create_index(
        op.f("ix_email_verification_tokens_token_hash"),
        "email_verification_tokens",
        ["token_hash"],
    )


def downgrade() -> None:
    op.drop_table("email_verification_tokens")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "preferred_language")
    op.drop_column("users", "country")
    op.drop_column("users", "date_of_birth")
