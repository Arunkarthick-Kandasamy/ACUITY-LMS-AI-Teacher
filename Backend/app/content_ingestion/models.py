from __future__ import annotations

import enum

from sqlalchemy import ForeignKey, Integer, String, Text
from app.common.compat import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin


class UploadStatus(str, enum.Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"


class DraftStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class ContentUpload(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "content_uploads"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=UploadStatus.PENDING, nullable=False, index=True)
    extracted_text: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)

    drafts: Mapped[list[CurriculumDraft]] = relationship(back_populates="upload", cascade="all, delete-orphan")


class CurriculumDraft(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "curriculum_drafts"

    upload_id: Mapped[str | None] = mapped_column(
        ForeignKey("content_uploads.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=DraftStatus.DRAFT, nullable=False, index=True)
    generated_data: Mapped[dict | None] = mapped_column(JSONB)
    course_id: Mapped[str | None] = mapped_column(
        ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True
    )

    upload: Mapped[ContentUpload | None] = relationship(back_populates="drafts")
