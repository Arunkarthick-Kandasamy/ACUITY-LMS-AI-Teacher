from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.types import MisconceptionCategory


class Misconception(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "misconceptions"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    concept_id: Mapped[str] = mapped_column(
        ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[MisconceptionCategory] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    detected_in_session_id: Mapped[str | None] = mapped_column(
        ForeignKey("teaching_sessions.id", ondelete="SET NULL"), index=True
    )
    evidence: Mapped[list] = mapped_column(JSONB, default=list)
    frequency: Mapped[int] = mapped_column(default=1, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped[StudentProfile] = relationship(back_populates="misconceptions")
    concept: Mapped[Concept] = relationship(back_populates="misconceptions")
    detected_in_session: Mapped[TeachingSession | None] = relationship(
        back_populates="misconceptions"
    )
