"""add student_linking_codes table

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-28

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "student_linking_codes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_linking_codes_code"), "student_linking_codes", ["code"], unique=True)
    op.create_index(op.f("ix_student_linking_codes_student_id"), "student_linking_codes", ["student_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_student_linking_codes_student_id"), table_name="student_linking_codes")
    op.drop_index(op.f("ix_student_linking_codes_code"), table_name="student_linking_codes")
    op.drop_table("student_linking_codes")
