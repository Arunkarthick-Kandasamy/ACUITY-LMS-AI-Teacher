from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from app.common.compat import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.types import ConceptContentType, LessonStatus, QuestionType


class Course(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "courses"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    total_duration_hours: Mapped[int] = mapped_column(nullable=False)
    default_deadline_days: Mapped[int] = mapped_column(nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    created_by_user: Mapped[User] = relationship(back_populates="courses_created")
    modules: Mapped[list[Module]] = relationship(back_populates="course", cascade="all, delete-orphan")
    enrollments: Mapped[list[StudentCourseEnrollment]] = relationship(back_populates="course")
    teaching_sessions: Mapped[list[TeachingSession]] = relationship(back_populates="course")


class Module(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "modules"
    __table_args__ = (UniqueConstraint("course_id", "order_index"),)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(nullable=False)
    estimated_duration_hours: Mapped[int | None] = mapped_column(Integer)

    course: Mapped[Course] = relationship(back_populates="modules")
    lessons: Mapped[list[Lesson]] = relationship(back_populates="module", cascade="all, delete-orphan")


class Lesson(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("module_id", "order_index"),)

    module_id: Mapped[str] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content_url: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(nullable=False)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[LessonStatus] = mapped_column(default=LessonStatus.DRAFT, nullable=False, index=True)

    module: Mapped[Module] = relationship(back_populates="lessons")
    concepts: Mapped[list[Concept]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    learning_objectives: Mapped[list[LearningObjective]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )
    lesson_progress_records: Mapped[list[LessonProgress]] = relationship(back_populates="lesson")
    teaching_sessions: Mapped[list[TeachingSession]] = relationship(back_populates="current_lesson")


class Concept(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "concepts"
    __table_args__ = (UniqueConstraint("lesson_id", "order_index"),)

    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(nullable=False)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)

    lesson: Mapped[Lesson] = relationship(back_populates="concepts")
    contents: Mapped[list[ConceptContent]] = relationship(back_populates="concept", cascade="all, delete-orphan")
    examples: Mapped[list[Example]] = relationship(back_populates="concept", cascade="all, delete-orphan")
    exercises: Mapped[list[Exercise]] = relationship(back_populates="concept", cascade="all, delete-orphan")
    knowledge_nodes: Mapped[list[KnowledgeNode]] = relationship(back_populates="concept")
    mastery_records: Mapped[list[MasteryRecord]] = relationship(back_populates="concept")
    misconceptions: Mapped[list[Misconception]] = relationship(back_populates="concept")
    teaching_sessions: Mapped[list[TeachingSession]] = relationship(back_populates="current_concept")
    enrollments: Mapped[list[StudentCourseEnrollment]] = relationship(back_populates="current_concept")


class ConceptContent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "concept_contents"
    __table_args__ = (UniqueConstraint("concept_id", "content_type", "order_index"),)

    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type: Mapped[ConceptContentType] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)

    concept: Mapped[Concept] = relationship(back_populates="contents")


class LearningObjective(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "learning_objectives"
    __table_args__ = (UniqueConstraint("lesson_id", "code"),)

    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    success_criterion: Mapped[dict | None] = mapped_column(JSONB)
    order_index: Mapped[int] = mapped_column(nullable=False)

    lesson: Mapped[Lesson] = relationship(back_populates="learning_objectives")
    knowledge_nodes: Mapped[list[KnowledgeNode]] = relationship(back_populates="objective")


class Example(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "examples"

    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(JSONB)

    concept: Mapped[Concept] = relationship(back_populates="examples")


class Exercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "exercises"

    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_type: Mapped[QuestionType] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5, nullable=False, index=True)
    order_index: Mapped[int] = mapped_column(nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(JSONB)

    concept: Mapped[Concept] = relationship(back_populates="exercises")
    attempts: Mapped[list[Attempt]] = relationship(back_populates="exercise")
