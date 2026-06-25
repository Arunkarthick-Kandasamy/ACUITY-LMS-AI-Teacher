from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.base import Base, UUIDMixin


class TeacherStudentAssignment(UUIDMixin, Base):
    __tablename__ = "teacher_student_assignments"
    __table_args__ = (
        UniqueConstraint("teacher_id", "student_id", name="uq_teacher_student"),
    )

    teacher_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    teacher: Mapped["User"] = relationship(
        foreign_keys="TeacherStudentAssignment.teacher_id",
        back_populates="teacher_student_assignments",
    )
    student: Mapped["StudentProfile"] = relationship(
        back_populates="teacher_assignments"
    )


class TeacherCourseAssignment(UUIDMixin, Base):
    __tablename__ = "teacher_course_assignments"
    __table_args__ = (
        UniqueConstraint("teacher_id", "course_id", name="uq_teacher_course"),
    )

    teacher_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), default="instructor", nullable=False)
    assigned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    teacher: Mapped["User"] = relationship(
        foreign_keys="TeacherCourseAssignment.teacher_id",
        back_populates="teacher_course_assignments",
    )
    course: Mapped["Course"] = relationship(back_populates="teacher_assignments")
