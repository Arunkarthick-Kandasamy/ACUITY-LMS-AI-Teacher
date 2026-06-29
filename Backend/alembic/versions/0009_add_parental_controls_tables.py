"""add parental_controls and sleep_schedules tables

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-28

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "parental_controls",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("daily_limit_minutes", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("break_interval_minutes", sa.Integer(), nullable=False, server_default="45"),
        sa.Column("break_duration_minutes", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("sleep_mode_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sleep_start_hour", sa.Integer(), nullable=False, server_default="22"),
        sa.Column("sleep_end_hour", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("content_restrictions", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
    )
    op.create_index(op.f("ix_parental_controls_student_id"), "parental_controls", ["student_id"])

    op.create_table(
        "sleep_schedules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sleep_schedules_student_id"), "sleep_schedules", ["student_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_sleep_schedules_student_id"), table_name="sleep_schedules")
    op.drop_table("sleep_schedules")
    op.drop_index(op.f("ix_parental_controls_student_id"), table_name="parental_controls")
    op.drop_table("parental_controls")
