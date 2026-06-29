"""add linking security improvements: status, audit log, failed_attempts

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-28

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add status, parent_email, requested_at, approved_at to parent_student_links
    op.add_column("parent_student_links", sa.Column("status", sa.String(20), nullable=False, server_default="pending"))
    op.add_column("parent_student_links", sa.Column("parent_email", sa.String(255), nullable=True))
    op.add_column("parent_student_links", sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("parent_student_links", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_parent_student_links_status"), "parent_student_links", ["status"])

    # Set requested_at to created_at for existing rows
    op.execute("UPDATE parent_student_links SET requested_at = created_at WHERE requested_at IS NULL")
    op.alter_column("parent_student_links", "requested_at", nullable=False)

    # Set status to 'active' for all existing links
    op.execute("UPDATE parent_student_links SET status = 'active' WHERE status = 'pending'")

    # Add created_at, updated_at to parent_student_links (TimestampMixin)
    op.add_column("parent_student_links", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column("parent_student_links", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

    # Add failed_attempts and code_cooldown_until to student_linking_codes
    op.add_column("student_linking_codes", sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("student_linking_codes", sa.Column("code_cooldown_until", sa.DateTime(timezone=True), nullable=True))

    # Create link_audit_logs table
    op.create_table(
        "link_audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("student_id", sa.Uuid(), nullable=True),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("parent_email", sa.String(255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["parent_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_link_audit_logs_action"), "link_audit_logs", ["action"])
    op.create_index(op.f("ix_link_audit_logs_actor_id"), "link_audit_logs", ["actor_id"])
    op.create_index(op.f("ix_link_audit_logs_student_id"), "link_audit_logs", ["student_id"])


def downgrade() -> None:
    op.drop_table("link_audit_logs")
    op.drop_column("student_linking_codes", "code_cooldown_until")
    op.drop_column("student_linking_codes", "failed_attempts")
    op.drop_column("parent_student_links", "updated_at")
    op.drop_column("parent_student_links", "created_at")
    op.drop_column("parent_student_links", "approved_at")
    op.drop_column("parent_student_links", "requested_at")
    op.drop_column("parent_student_links", "parent_email")
    op.drop_index(op.f("ix_parent_student_links_status"), "parent_student_links")
    op.drop_column("parent_student_links", "status")
