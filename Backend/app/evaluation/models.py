from __future__ import annotations

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.common.base import Base, TimestampMixin, UUIDMixin


class GraphTrace(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "graph_traces"

    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("teaching_sessions.id", ondelete="SET NULL"), index=True
    )
    student_id: Mapped[str | None] = mapped_column(index=True)
    concept_id: Mapped[str | None] = mapped_column(index=True)
    scenario_label: Mapped[str | None] = mapped_column(String(100))
    trace_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    node_transitions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    total_duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    token_usage: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    model_calls: Mapped[int] = mapped_column(Integer, default=0)
    final_action: Mapped[str | None] = mapped_column(String(50))
    final_mastery: Mapped[float] = mapped_column(Float, default=0.0)
    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TeacherMetricsSnapshot(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "teacher_metrics_snapshots"

    snapshot_label: Mapped[str | None] = mapped_column(String(100), index=True)
    period_start: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    concepts_taught: Mapped[int] = mapped_column(Integer, default=0)
    concept_mastery_rate: Mapped[float] = mapped_column(Float, default=0.0)
    remediation_rate: Mapped[float] = mapped_column(Float, default=0.0)
    misconception_detection_rate: Mapped[float] = mapped_column(Float, default=0.0)
    prerequisite_routing_frequency: Mapped[float] = mapped_column(Float, default=0.0)
    session_completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_mastery_gain: Mapped[float] = mapped_column(Float, default=0.0)
    avg_execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    total_model_calls: Mapped[int] = mapped_column(Integer, default=0)
    breakdown: Mapped[dict | None] = mapped_column(JSONB, default=dict)
