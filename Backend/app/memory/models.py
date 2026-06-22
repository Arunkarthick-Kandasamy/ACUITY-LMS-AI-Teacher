from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin


class StudentMemory(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "student_memories"
    __table_args__ = (UniqueConstraint("student_id", "key"),)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=0.5, nullable=False, index=True)

    student: Mapped[StudentProfile] = relationship(back_populates="memories")


class MemoryEntry(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "memory_entries"
    __table_args__ = (UniqueConstraint("student_id", "memory_key", "memory_text"),)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    memory_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    source_session_id: Mapped[str | None] = mapped_column(
        ForeignKey("teaching_sessions.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    student: Mapped[StudentProfile] = relationship(back_populates="memory_entries")
