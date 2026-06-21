from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.common.types import SessionState


class StartSessionRequest(BaseModel):
    course_id: str
    lesson_id: str | None = None
    concept_id: str | None = None


class SessionResponse(BaseModel):
    session_id: str
    student_id: str
    course_id: str
    course_title: str | None = None
    current_lesson_id: str | None = None
    current_concept_id: str | None = None
    state: SessionState
    context: dict = Field(default_factory=dict)
    started_at: datetime
    last_activity_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class EndSessionRequest(BaseModel):
    state: SessionState | None = Field(default=None, description="Optional final state, defaults to completed")


class SessionHistoryItem(BaseModel):
    session_id: str
    course_id: str
    course_title: str | None = None
    state: SessionState
    started_at: datetime
    last_activity_at: datetime
    completed_at: datetime | None = None
    duration_minutes: int | None = None

    model_config = {"from_attributes": True}
