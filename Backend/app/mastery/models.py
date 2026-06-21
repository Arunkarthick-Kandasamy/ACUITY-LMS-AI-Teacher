from __future__ import annotations

from sqlalchemy import DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin


class MasteryRecord(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "mastery_records"
    __table_args__ = (UniqueConstraint("student_id", "concept_id"),)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    concept_id: Mapped[str] = mapped_column(
        ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mastery_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    last_attempted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    total_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    consecutive_correct: Mapped[int] = mapped_column(default=0, nullable=False)
    next_review_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), index=True)

    student: Mapped[StudentProfile] = relationship(back_populates="mastery_records")
    concept: Mapped[Concept] = relationship(back_populates="mastery_records")
