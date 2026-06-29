from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin


class Badge(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "badges"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="milestone")  # milestone, mastery, streak, special
    criteria: Mapped[str] = mapped_column(Text, nullable=True)

    achievements: Mapped[list[UserAchievement]] = relationship(back_populates="badge", cascade="all, delete-orphan")


class UserAchievement(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_achievements"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    badge_id: Mapped[str] = mapped_column(ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True)
    earned_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    badge: Mapped[Badge] = relationship(back_populates="achievements")


class Streak(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "streaks"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
