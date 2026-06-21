from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.types import LessonProgressStatus, SessionState


class TeachingSession(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "teaching_sessions"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    current_concept_id: Mapped[str | None] = mapped_column(
        ForeignKey("concepts.id", ondelete="SET NULL"), index=True
    )
    current_lesson_id: Mapped[str | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    state: Mapped[SessionState] = mapped_column(default=SessionState.ACTIVE, nullable=False)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_activity_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped[StudentProfile] = relationship(back_populates="teaching_sessions")
    course: Mapped[Course] = relationship(back_populates="teaching_sessions")
    current_concept: Mapped[Concept | None] = relationship(
        back_populates="teaching_sessions", foreign_keys="TeachingSession.current_concept_id"
    )
    current_lesson: Mapped[Lesson | None] = relationship(
        back_populates="teaching_sessions", foreign_keys="TeachingSession.current_lesson_id"
    )
    attempts: Mapped[list[Attempt]] = relationship(back_populates="teaching_session")
    misconceptions: Mapped[list[Misconception]] = relationship(back_populates="detected_in_session")


class LessonProgress(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("student_id", "lesson_id"),)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[str] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[LessonProgressStatus] = mapped_column(
        default=LessonProgressStatus.NOT_STARTED, nullable=False, index=True
    )
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    time_spent_seconds: Mapped[int] = mapped_column(default=0)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    student: Mapped[StudentProfile] = relationship(back_populates="lesson_progress_records")
    lesson: Mapped[Lesson] = relationship(back_populates="lesson_progress_records")


class Attempt(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "attempts"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id: Mapped[str] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    teaching_session_id: Mapped[str] = mapped_column(
        ForeignKey("teaching_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    response: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer)
    attempted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    attempt_number: Mapped[int] = mapped_column(nullable=False)
    ai_feedback: Mapped[str | None] = mapped_column(Text)
    attempt_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    student: Mapped[StudentProfile] = relationship(back_populates="attempts")
    exercise: Mapped[Exercise] = relationship(back_populates="attempts")
    teaching_session: Mapped[TeachingSession] = relationship(back_populates="attempts")
