"""Add title and report_data columns to reports table.

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-22 10:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("title", sa.String(300), nullable=True))
    op.add_column("reports", sa.Column("report_data", postgresql.JSONB()))


def downgrade() -> None:
    op.drop_column("reports", "report_data")
    op.drop_column("reports", "title")
