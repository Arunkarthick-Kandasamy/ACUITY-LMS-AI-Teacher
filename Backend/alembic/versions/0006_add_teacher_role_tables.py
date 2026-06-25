"""Add teacher role and tables.

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-25 12:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "teacher_student_assignments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("teacher_id", sa.String(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("teacher_id", "student_id", name="uq_teacher_student"),
    )
    op.create_index(
        op.f("ix_teacher_student_assignments_teacher_id"),
        "teacher_student_assignments",
        ["teacher_id"],
    )
    op.create_index(
        op.f("ix_teacher_student_assignments_student_id"),
        "teacher_student_assignments",
        ["student_id"],
    )

    op.create_table(
        "teacher_course_assignments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("teacher_id", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="instructor"),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("teacher_id", "course_id", name="uq_teacher_course"),
    )
    op.create_index(
        op.f("ix_teacher_course_assignments_teacher_id"),
        "teacher_course_assignments",
        ["teacher_id"],
    )
    op.create_index(
        op.f("ix_teacher_course_assignments_course_id"),
        "teacher_course_assignments",
        ["course_id"],
    )


def downgrade() -> None:
    op.drop_table("teacher_course_assignments")
    op.drop_table("teacher_student_assignments")
