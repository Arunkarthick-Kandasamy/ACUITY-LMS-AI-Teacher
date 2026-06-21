from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.common.types import PaceStatus


class GenerateScheduleRequest(BaseModel):
    enrollment_id: str


class PacingStatusResponse(BaseModel):
    enrollment_id: str
    course_id: str
    course_title: str | None = None
    schedule_id: str
    current_week: int
    target_lessons_per_week: int
    pace_status: PaceStatus
    last_pacing_adjustment_at: datetime | None = None

    model_config = {"from_attributes": True}


class PacingUpdateRequest(BaseModel):
    enrollment_id: str
    pace_status: PaceStatus


class PacingUpdateResponse(BaseModel):
    schedule_id: str
    enrollment_id: str
    pace_status: PaceStatus
    last_pacing_adjustment_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeleteMessage(BaseModel):
    message: str
