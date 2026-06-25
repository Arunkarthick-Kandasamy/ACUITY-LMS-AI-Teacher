"""Create all ENUM types and tables.

Revision ID: 0001
Revises:
Create Date: 2026-06-21 20:45:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'student', 'parent', 'teacher')")
    op.execute("CREATE TYPE lesson_status AS ENUM ('draft', 'published', 'archived')")
    op.execute(
        "CREATE TYPE concept_content_type AS ENUM "
        "('explanation', 'example', 'visualization', 'analogy', 'summary')"
    )
    op.execute(
        "CREATE TYPE question_type AS ENUM ('mcq', 'multi_select', 'short_answer', 'fill_blank')"
    )
    op.execute(
        "CREATE TYPE enrollment_status AS ENUM ('active', 'paused', 'completed', 'dropped')"
    )
    op.execute(
        "CREATE TYPE session_state AS ENUM ('active', 'paused', 'completed', 'interrupted')"
    )
    op.execute(
        "CREATE TYPE lesson_progress_status AS ENUM "
        "('not_started', 'in_progress', 'completed', 'skipped')"
    )
    op.execute(
        "CREATE TYPE misconception_category AS ENUM "
        "('procedural', 'conceptual', 'factual', 'careless')"
    )
    op.execute(
        "CREATE TYPE edge_relationship AS ENUM ('requires', 'reinforces', 'contains')"
    )
    op.execute("CREATE TYPE pace_status AS ENUM ('on_track', 'behind', 'ahead')")
    op.execute("CREATE TYPE report_type AS ENUM ('weekly', 'monthly', 'milestone')")
    op.execute("CREATE TYPE node_type AS ENUM ('concept', 'objective')")

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", postgresql.ENUM("admin", "student", "parent", name="user_role", create_type=False), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("grade_level", sa.String(50), nullable=True),
        sa.Column("avg_session_duration_minutes", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("current_streak_days", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"])

    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("total_duration_hours", sa.Integer(), nullable=False),
        sa.Column("default_deadline_days", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"],),
    )
    op.create_index("ix_courses_code", "courses", ["code"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(50), nullable=False),
        sa.Column("old_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])

    op.create_table(
        "parent_student_links",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["parent_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("parent_id", "student_id"),
    )
    op.create_index("ix_parent_student_links_parent_id", "parent_student_links", ["parent_id"])
    op.create_index("ix_parent_student_links_student_id", "parent_student_links", ["student_id"])

    op.create_table(
        "modules",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("estimated_duration_hours", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("course_id", "order_index"),
    )
    op.create_index("ix_modules_course_id", "modules", ["course_id"])

    # -- tables that concepts depends on (lessons -> modules -> courses) --
    op.create_table(
        "lessons",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("module_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content_url", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("status", postgresql.ENUM("draft", "published", "archived", name="lesson_status", create_type=False), server_default=sa.text("'draft'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("module_id", "order_index"),
    )
    op.create_index("ix_lessons_module_id", "lessons", ["module_id"])
    op.create_index("ix_lessons_status", "lessons", ["status"])

    op.create_table(
        "concepts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("lesson_id", "order_index"),
    )
    op.create_index("ix_concepts_lesson_id", "concepts", ["lesson_id"])

    op.create_table(
        "learning_objectives",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("success_criterion", postgresql.JSONB(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("lesson_id", "code"),
    )
    op.create_index("ix_learning_objectives_lesson_id", "learning_objectives", ["lesson_id"])
    op.create_index("ix_learning_objectives_code", "learning_objectives", ["code"])

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("status", postgresql.ENUM("not_started", "in_progress", "completed", "skipped", name="lesson_progress_status", create_type=False), server_default=sa.text("'not_started'"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_spent_seconds", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("completion_percentage", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("student_id", "lesson_id"),
    )
    op.create_index("ix_lesson_progress_student_id", "lesson_progress", ["student_id"])
    op.create_index("ix_lesson_progress_lesson_id", "lesson_progress", ["lesson_id"])
    op.create_index("ix_lesson_progress_status", "lesson_progress", ["status"])

    op.create_table(
        "concept_contents",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("content_type", postgresql.ENUM("explanation", "example", "visualization", "analogy", "summary", name="concept_content_type", create_type=False), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("concept_id", "content_type", "order_index"),
    )
    op.create_index("ix_concept_contents_concept_id", "concept_contents", ["concept_id"])

    op.create_table(
        "examples",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_examples_concept_id", "examples", ["concept_id"])

    op.create_table(
        "exercises",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("question_type", postgresql.ENUM("mcq", "multi_select", "short_answer", "fill_blank", name="question_type", create_type=False), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(), nullable=True),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.Float(), server_default=sa.text("0.5"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_exercises_concept_id", "exercises", ["concept_id"])
    op.create_index("ix_exercises_difficulty", "exercises", ["difficulty"])

    op.create_table(
        "knowledge_nodes",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=True),
        sa.Column("objective_id", sa.Uuid(), nullable=True),
        sa.Column("node_type", postgresql.ENUM("concept", "objective", name="node_type", create_type=False), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["objective_id"], ["learning_objectives.id"], ondelete="SET NULL"),
        sa.CheckConstraint("concept_id IS NOT NULL OR objective_id IS NOT NULL"),
    )
    op.create_index("ix_knowledge_nodes_concept_id", "knowledge_nodes", ["concept_id"])
    op.create_index("ix_knowledge_nodes_objective_id", "knowledge_nodes", ["objective_id"])
    op.create_index("ix_knowledge_nodes_node_type", "knowledge_nodes", ["node_type"])
    op.create_index("ix_knowledge_nodes_label", "knowledge_nodes", ["label"])

    op.create_table(
        "teaching_sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("current_concept_id", sa.Uuid(), nullable=True),
        sa.Column("current_lesson_id", sa.Uuid(), nullable=True),
        sa.Column("state", postgresql.ENUM("active", "paused", "completed", "interrupted", name="session_state", create_type=False), server_default=sa.text("'active'"), nullable=False),
        sa.Column("context", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["current_concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["current_lesson_id"], ["lessons.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_teaching_sessions_student_id", "teaching_sessions", ["student_id"])
    op.create_index("ix_teaching_sessions_course_id", "teaching_sessions", ["course_id"])
    op.create_index("ix_teaching_sessions_current_concept_id", "teaching_sessions", ["current_concept_id"])
    op.create_index("ix_teaching_sessions_current_lesson_id", "teaching_sessions", ["current_lesson_id"])

    op.create_table(
        "mastery_records",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("mastery_level", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("last_attempted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("consecutive_correct", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("student_id", "concept_id"),
    )
    op.create_index("ix_mastery_records_student_id", "mastery_records", ["student_id"])
    op.create_index("ix_mastery_records_concept_id", "mastery_records", ["concept_id"])
    op.create_index("ix_mastery_records_mastery_level", "mastery_records", ["mastery_level"])
    op.create_index("ix_mastery_records_next_review_at", "mastery_records", ["next_review_at"])

    op.create_table(
        "knowledge_edges",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_node_id", sa.Uuid(), nullable=False),
        sa.Column("target_node_id", sa.Uuid(), nullable=False),
        sa.Column("relationship", postgresql.ENUM("requires", "reinforces", "contains", name="edge_relationship", create_type=False), nullable=False),
        sa.Column("weight", sa.Float(), server_default=sa.text("1.0"), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["source_node_id"], ["knowledge_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_node_id"], ["knowledge_nodes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("source_node_id", "target_node_id", "relationship"),
        sa.CheckConstraint("source_node_id <> target_node_id"),
    )
    op.create_index("ix_knowledge_edges_source_node_id", "knowledge_edges", ["source_node_id"])
    op.create_index("ix_knowledge_edges_target_node_id", "knowledge_edges", ["target_node_id"])

    op.create_table(
        "attempts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("teaching_session_id", sa.Uuid(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("time_taken_seconds", sa.Integer(), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("ai_feedback", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teaching_session_id"], ["teaching_sessions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_attempts_student_id", "attempts", ["student_id"])
    op.create_index("ix_attempts_exercise_id", "attempts", ["exercise_id"])
    op.create_index("ix_attempts_teaching_session_id", "attempts", ["teaching_session_id"])

    op.create_table(
        "misconceptions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("category", postgresql.ENUM("procedural", "conceptual", "factual", "careless", name="misconception_category", create_type=False), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("detected_in_session_id", sa.Uuid(), nullable=True),
        sa.Column("evidence", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("frequency", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("is_resolved", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["detected_in_session_id"], ["teaching_sessions.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_misconceptions_student_id", "misconceptions", ["student_id"])
    op.create_index("ix_misconceptions_concept_id", "misconceptions", ["concept_id"])
    op.create_index("ix_misconceptions_detected_in_session_id", "misconceptions", ["detected_in_session_id"])

    op.create_table(
        "student_course_enrollments",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", postgresql.ENUM("active", "paused", "completed", "dropped", name="enrollment_status", create_type=False), server_default=sa.text("'active'"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_completion_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_concept_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["current_concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("student_id", "course_id", name="uq_student_active_enrollment"),
    )
    op.create_index("ix_student_course_enrollments_student_id", "student_course_enrollments", ["student_id"])
    op.create_index("ix_student_course_enrollments_course_id", "student_course_enrollments", ["course_id"])
    op.create_index("ix_student_course_enrollments_status", "student_course_enrollments", ["status"])
    op.create_index("ix_student_course_enrollments_current_concept_id", "student_course_enrollments", ["current_concept_id"])

    op.create_table(
        "student_memories",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("importance", sa.Float(), server_default=sa.text("0.5"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("student_id", "key"),
    )
    op.create_index("ix_student_memories_student_id", "student_memories", ["student_id"])
    op.create_index("ix_student_memories_importance", "student_memories", ["importance"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("report_type", postgresql.ENUM("weekly", "monthly", "milestone", name="report_type", create_type=False), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("recommendations", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("pdf_url", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_reports_student_id", "reports", ["student_id"])
    op.create_index("ix_reports_parent_id", "reports", ["parent_id"])
    op.create_index("ix_reports_report_type", "reports", ["report_type"])

    op.create_table(
        "course_schedules",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("enrollment_id", sa.Uuid(), nullable=False),
        sa.Column("target_lessons_per_week", sa.Integer(), server_default=sa.text("3"), nullable=False),
        sa.Column("current_week", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("pace_status", postgresql.ENUM("on_track", "behind", "ahead", name="pace_status", create_type=False), server_default=sa.text("'on_track'"), nullable=False),
        sa.Column("last_pacing_adjustment_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("milestones", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["enrollment_id"], ["student_course_enrollments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("enrollment_id"),
    )
    op.create_index("ix_course_schedules_enrollment_id", "course_schedules", ["enrollment_id"])
    op.create_index("ix_course_schedules_pace_status", "course_schedules", ["pace_status"])


def downgrade() -> None:
    op.drop_table("course_schedules")
    op.drop_table("reports")
    op.drop_table("student_memories")
    op.drop_table("student_course_enrollments")
    op.drop_table("misconceptions")
    op.drop_table("attempts")
    op.drop_table("knowledge_edges")
    op.drop_table("mastery_records")
    op.drop_table("teaching_sessions")
    op.drop_table("knowledge_nodes")
    op.drop_table("exercises")
    op.drop_table("examples")
    op.drop_table("concept_contents")
    op.drop_table("lesson_progress")
    op.drop_table("learning_objectives")
    op.drop_table("concepts")
    op.drop_table("lessons")
    op.drop_table("modules")
    op.drop_table("parent_student_links")
    op.drop_table("audit_logs")
    op.drop_table("courses")
    op.drop_table("student_profiles")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS node_type")
    op.execute("DROP TYPE IF EXISTS report_type")
    op.execute("DROP TYPE IF EXISTS pace_status")
    op.execute("DROP TYPE IF EXISTS edge_relationship")
    op.execute("DROP TYPE IF EXISTS misconception_category")
    op.execute("DROP TYPE IF EXISTS lesson_progress_status")
    op.execute("DROP TYPE IF EXISTS session_state")
    op.execute("DROP TYPE IF EXISTS enrollment_status")
    op.execute("DROP TYPE IF EXISTS question_type")
    op.execute("DROP TYPE IF EXISTS concept_content_type")
    op.execute("DROP TYPE IF EXISTS lesson_status")
    op.execute("DROP TYPE IF EXISTS user_role")
