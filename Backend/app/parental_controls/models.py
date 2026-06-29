from __future__ import annotations

from datetime import time

from sqlalchemy import Boolean, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin


class ParentalControl(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "parental_controls"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    daily_limit_minutes: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    break_interval_minutes: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    sleep_mode_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sleep_start_hour: Mapped[int] = mapped_column(Integer, default=22, nullable=False)
    sleep_end_hour: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    content_restrictions: Mapped[str | None] = mapped_column(String(500), nullable=True)

    student: Mapped[StudentProfile] = relationship()  # noqa: F821


class SleepSchedule(UUIDMixin, Base):
    __tablename__ = "sleep_schedules"

    student_id: Mapped[str] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
