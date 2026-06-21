from __future__ import annotations

from datetime import date

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.types import EnrollmentStatus, PaceStatus


class StudentCourseEnrollment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "student_course_enrollments"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    enrolled_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        default=EnrollmentStatus.ACTIVE, nullable=False, index=True
    )
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    target_completion_date: Mapped[date | None] = mapped_column(Date)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    current_concept_id: Mapped[str | None] = mapped_column(
        ForeignKey("concepts.id", ondelete="SET NULL"), index=True
    )

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_active_enrollment"),
    )

    student: Mapped[StudentProfile] = relationship(back_populates="enrollments")
    course: Mapped[Course] = relationship(back_populates="enrollments")
    current_concept: Mapped[Concept | None] = relationship(back_populates="enrollments")
    schedule: Mapped[CourseSchedule | None] = relationship(back_populates="enrollment", uselist=False)


class CourseSchedule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "course_schedules"
    __table_args__ = (UniqueConstraint("enrollment_id"),)

    enrollment_id: Mapped[str] = mapped_column(
        ForeignKey("student_course_enrollments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_lessons_per_week: Mapped[int] = mapped_column(default=3, nullable=False)
    current_week: Mapped[int] = mapped_column(default=1, nullable=False)
    pace_status: Mapped[PaceStatus] = mapped_column(
        default=PaceStatus.ON_TRACK, nullable=False, index=True
    )
    last_pacing_adjustment_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    milestones: Mapped[list] = mapped_column(JSONB, default=list)

    enrollment: Mapped[StudentCourseEnrollment] = relationship(back_populates="schedule")
