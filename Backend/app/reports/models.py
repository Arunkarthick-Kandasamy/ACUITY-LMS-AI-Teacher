from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.base import Base, UUIDMixin
from app.common.types import ReportType


class Report(UUIDMixin, Base):
    __tablename__ = "reports"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    report_type: Mapped[ReportType] = mapped_column(nullable=False, index=True)
    generated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    summary: Mapped[str | None] = mapped_column(Text)
    recommendations: Mapped[list] = mapped_column(JSONB, default=list)
    pdf_url: Mapped[str | None] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    student: Mapped[StudentProfile] = relationship(back_populates="reports")
    parent: Mapped[User | None] = relationship(back_populates="reports_as_parent")
