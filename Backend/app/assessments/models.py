from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from app.common.compat import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.types import AssessmentType, QuestionType


class Assessment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessments"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    lesson_id: Mapped[str | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL"), index=True
    )
    module_id: Mapped[str | None] = mapped_column(
        ForeignKey("modules.id", ondelete="SET NULL"), index=True
    )
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assessment_type: Mapped[AssessmentType] = mapped_column(nullable=False)
    passing_score: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    time_limit: Mapped[int | None] = mapped_column(Integer)
    max_attempts: Mapped[int] = mapped_column(default=1, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    course: Mapped["Course"] = relationship(back_populates="assessments")
    lesson: Mapped["Lesson | None"] = relationship(back_populates="assessments")
    module: Mapped["Module | None"] = relationship(back_populates="assessments")
    creator: Mapped["User"] = relationship(back_populates="assessments_created")
    questions: Mapped[list[AssessmentQuestion]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    attempts: Mapped[list[AssessmentAttempt]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentQuestion(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessment_questions"
    __table_args__ = (UniqueConstraint("assessment_id", "order_index"),)

    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_type: Mapped[QuestionType] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    marks: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(nullable=False)

    assessment: Mapped[Assessment] = relationship(back_populates="questions")
    responses: Mapped[list[AssessmentResponse]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class AssessmentAttempt(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessment_attempts"

    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    attempt_number: Mapped[int] = mapped_column(nullable=False)

    assessment: Mapped[Assessment] = relationship(back_populates="attempts")
    student: Mapped["StudentProfile"] = relationship(back_populates="assessment_attempts")
    responses: Mapped[list[AssessmentResponse]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan"
    )


class AssessmentResponse(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessment_responses"

    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    response: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    feedback: Mapped[str | None] = mapped_column(Text)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer)

    attempt: Mapped[AssessmentAttempt] = relationship(back_populates="responses")
    question: Mapped[AssessmentQuestion] = relationship(back_populates="responses")


class QuestionBank(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "question_bank"

    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[str | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL"), index=True
    )
    concept_id: Mapped[str | None] = mapped_column(
        ForeignKey("concepts.id", ondelete="SET NULL"), index=True
    )
    question_type: Mapped[QuestionType] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    marks: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(JSONB)

    course: Mapped["Course"] = relationship(back_populates="question_bank_items")
