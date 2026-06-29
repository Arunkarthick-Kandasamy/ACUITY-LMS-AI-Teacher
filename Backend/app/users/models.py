from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.compat import JSONB
from app.common.types import UserRole


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", create_constraint=False,
               validate_strings=True,
               values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    student_profile: Mapped[StudentProfile | None] = relationship(back_populates="user", uselist=False)
    parent_links: Mapped[list[ParentStudentLink]] = relationship(
        back_populates="parent", foreign_keys="ParentStudentLink.parent_id"
    )
    courses_created: Mapped[list[Course]] = relationship(back_populates="created_by_user")
    assessments_created: Mapped[list[Assessment]] = relationship(back_populates="creator")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")
    reports_as_parent: Mapped[list[Report]] = relationship(
        back_populates="parent", foreign_keys="Report.parent_id"
    )
    teacher_student_assignments: Mapped[list[TeacherStudentAssignment]] = relationship(
        back_populates="teacher", foreign_keys="TeacherStudentAssignment.teacher_id"
    )
    teacher_course_assignments: Mapped[list[TeacherCourseAssignment]] = relationship(
        back_populates="teacher", foreign_keys="TeacherCourseAssignment.teacher_id"
    )


class StudentProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_level: Mapped[str | None] = mapped_column(String(50))
    avg_session_duration_minutes: Mapped[int] = mapped_column(default=0)
    current_streak_days: Mapped[int] = mapped_column(default=0)
    profile_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    user: Mapped[User] = relationship(back_populates="student_profile")
    linking_codes: Mapped[list[StudentLinkingCode]] = relationship(back_populates="student")
    parent_links: Mapped[list[ParentStudentLink]] = relationship(back_populates="student")
    enrollments: Mapped[list[StudentCourseEnrollment]] = relationship(back_populates="student")
    teaching_sessions: Mapped[list[TeachingSession]] = relationship(back_populates="student")
    lesson_progress_records: Mapped[list[LessonProgress]] = relationship(back_populates="student")
    attempts: Mapped[list[Attempt]] = relationship(back_populates="student")
    mastery_records: Mapped[list[MasteryRecord]] = relationship(back_populates="student")
    misconceptions: Mapped[list[Misconception]] = relationship(back_populates="student")
    memories: Mapped[list[StudentMemory]] = relationship(back_populates="student")
    memory_entries: Mapped[list[MemoryEntry]] = relationship(back_populates="student")
    reports: Mapped[list[Report]] = relationship(back_populates="student")
    assessment_attempts: Mapped[list[AssessmentAttempt]] = relationship(back_populates="student")
    teacher_assignments: Mapped[list[TeacherStudentAssignment]] = relationship(back_populates="student")


class StudentLinkingCode(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "student_linking_codes"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    code_cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    student: Mapped[StudentProfile] = relationship(back_populates="linking_codes")


class ParentStudentLink(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "parent_student_links"
    __table_args__ = (UniqueConstraint("parent_id", "student_id"),)

    parent_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    parent_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    parent: Mapped[User] = relationship(back_populates="parent_links", foreign_keys="ParentStudentLink.parent_id")
    student: Mapped[StudentProfile] = relationship(
        back_populates="parent_links", foreign_keys="ParentStudentLink.student_id"
    )


class LinkAuditLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "link_audit_logs"

    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    parent_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
