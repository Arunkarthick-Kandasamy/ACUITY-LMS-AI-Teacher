from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.compat import JSONB


class CourseStatus(str, enum.Enum):
    DRAFT = "draft"
    TRAINING = "training"
    REVIEW = "review"
    READY = "ready"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class PipelineStageName(str, enum.Enum):
    UPLOAD = "upload"
    EXTRACT = "extract"
    UNDERSTAND = "understand"
    VALIDATE = "validate"
    PROFILE = "profile"
    STRUCTURE = "structure"
    GENERATE = "generate"
    REVIEW = "review"
    SIMULATE = "simulate"
    DEPLOY = "deploy"


class StageStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


STAGE_ORDER = [
    PipelineStageName.UPLOAD,
    PipelineStageName.EXTRACT,
    PipelineStageName.UNDERSTAND,
    PipelineStageName.VALIDATE,
    PipelineStageName.PROFILE,
    PipelineStageName.STRUCTURE,
    PipelineStageName.GENERATE,
    PipelineStageName.REVIEW,
    PipelineStageName.SIMULATE,
    PipelineStageName.DEPLOY,
]

STAGE_LABELS = {
    "upload": "Upload Knowledge",
    "extract": "Extract Text Content",
    "understand": "Understand & Build Knowledge Graph",
    "validate": "Validate Understanding",
    "profile": "Generate Teaching Profile",
    "structure": "Generate Course Structure",
    "generate": "Generate Lessons & Assessments",
    "review": "Review & Refine",
    "simulate": "Simulation & Testing",
    "deploy": "Publish Course",
}


class Course(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_teachers"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default=CourseStatus.DRAFT, nullable=False, index=True
    )
    course_id: Mapped[str | None] = mapped_column(
        ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    knowledge_sources: Mapped[dict | None] = mapped_column(JSONB)
    knowledge_graph_data: Mapped[dict | None] = mapped_column(JSONB)
    teaching_profile: Mapped[dict | None] = mapped_column(JSONB)
    course_structure: Mapped[dict | None] = mapped_column(JSONB)
    simulation_results: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)

    stages: Mapped[list[PipelineStage]] = relationship(
        back_populates="course", cascade="all, delete-orphan",
        order_by="PipelineStage.created_at",
    )
    sources: Mapped[list[KnowledgeSource]] = relationship(
        back_populates="course", cascade="all, delete-orphan",
    )

    @property
    def stage_progress(self) -> dict:
        stages_data = self.stages or []
        completed = sum(1 for s in stages_data if s.status == StageStatus.COMPLETED.value)
        total = len(STAGE_ORDER)
        return {"completed": completed, "total": total, "pct": round(completed / total * 100) if total else 0}


class PipelineStage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "pipeline_stages"

    course_id: Mapped[str] = mapped_column(
        "ai_teacher_id", ForeignKey("ai_teachers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=StageStatus.PENDING, nullable=False
    )
    progress_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    output_data: Mapped[dict | None] = mapped_column(JSONB)
    stage_logs: Mapped[list | None] = mapped_column(JSONB)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    course: Mapped[Course] = relationship(back_populates="stages")

    @property
    def duration_seconds(self) -> int | None:
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        if self.started_at and self.status == StageStatus.IN_PROGRESS.value:
            from datetime import datetime, timezone
            return int((datetime.now(timezone.utc) - self.started_at).total_seconds())
        return None


class KnowledgeSource(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_sources"

    course_id: Mapped[str] = mapped_column(
        "ai_teacher_id", ForeignKey("ai_teachers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text)

    course: Mapped[Course] = relationship(back_populates="sources")
