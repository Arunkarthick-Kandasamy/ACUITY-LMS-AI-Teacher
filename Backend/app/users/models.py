from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.types import UserRole


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    student_profile: Mapped[StudentProfile | None] = relationship(back_populates="user", uselist=False)
    parent_links: Mapped[list[ParentStudentLink]] = relationship(
        back_populates="parent", foreign_keys="ParentStudentLink.parent_id"
    )
    courses_created: Mapped[list[Course]] = relationship(back_populates="created_by_user")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")
    reports_as_parent: Mapped[list[Report]] = relationship(
        back_populates="parent", foreign_keys="Report.parent_id"
    )


class StudentProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_level: Mapped[str | None] = mapped_column(String(50))
    avg_session_duration_minutes: Mapped[int] = mapped_column(default=0)
    current_streak_days: Mapped[int] = mapped_column(default=0)
    profile_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    user: Mapped[User] = relationship(back_populates="student_profile")
    parent_links: Mapped[list[ParentStudentLink]] = relationship(back_populates="student")
    enrollments: Mapped[list[StudentCourseEnrollment]] = relationship(back_populates="student")
    teaching_sessions: Mapped[list[TeachingSession]] = relationship(back_populates="student")
    lesson_progress_records: Mapped[list[LessonProgress]] = relationship(back_populates="student")
    attempts: Mapped[list[Attempt]] = relationship(back_populates="student")
    mastery_records: Mapped[list[MasteryRecord]] = relationship(back_populates="student")
    misconceptions: Mapped[list[Misconception]] = relationship(back_populates="student")
    memories: Mapped[list[StudentMemory]] = relationship(back_populates="student")
    reports: Mapped[list[Report]] = relationship(back_populates="student")


class ParentStudentLink(UUIDMixin, Base):
    __tablename__ = "parent_student_links"
    __table_args__ = (UniqueConstraint("parent_id", "student_id"),)

    parent_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    parent: Mapped[User] = relationship(back_populates="parent_links", foreign_keys="ParentStudentLink.parent_id")
    student: Mapped[StudentProfile] = relationship(
        back_populates="parent_links", foreign_keys="ParentStudentLink.student_id"
    )
