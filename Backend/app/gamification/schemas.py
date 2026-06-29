from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BadgeCreate(BaseModel):
    name: str
    description: str | None = None
    icon_url: str | None = None
    category: str = "milestone"
    criteria: str | None = None


class BadgeResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    icon_url: str | None = None
    category: str
    criteria: str | None = None

    model_config = {"from_attributes": True}


class AchievementResponse(BaseModel):
    id: str
    badge_id: str
    badge_name: str = ""
    badge_icon_url: str | None = None
    badge_category: str = ""
    earned_at: datetime

    model_config = {"from_attributes": True}


class StreakResponse(BaseModel):
    user_id: str
    current_streak: int
    longest_streak: int
    last_activity_date: datetime | None = None

    model_config = {"from_attributes": True}


class AwardBadgeRequest(BaseModel):
    badge_id: str
