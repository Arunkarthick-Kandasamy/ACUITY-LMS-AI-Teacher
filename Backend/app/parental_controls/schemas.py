from __future__ import annotations

from pydantic import BaseModel, Field


class ParentalControlResponse(BaseModel):
    student_id: str
    daily_limit_minutes: int
    break_interval_minutes: int
    break_duration_minutes: int
    sleep_mode_enabled: bool
    sleep_start_hour: int
    sleep_end_hour: int
    content_restrictions: str | None = None

    model_config = {"from_attributes": True}


class ParentalControlUpdate(BaseModel):
    daily_limit_minutes: int | None = Field(None, ge=15, le=480)
    break_interval_minutes: int | None = Field(None, ge=15, le=120)
    break_duration_minutes: int | None = Field(None, ge=1, le=30)
    sleep_mode_enabled: bool | None = None
    sleep_start_hour: int | None = Field(None, ge=0, le=23)
    sleep_end_hour: int | None = Field(None, ge=0, le=23)
    content_restrictions: str | None = None


class MessageResponse(BaseModel):
    message: str
