from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.common.types import EnrollmentStatus


class EnrollmentCreate(BaseModel):
    course_id: str


class EnrollmentResponse(BaseModel):
    enrollment_id: str
    student_id: str
    course_id: str
    course_title: str | None = None
    status: EnrollmentStatus
    enrolled_at: datetime
    started_at: datetime | None = None
    target_completion_date: date | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class EnrollmentListResponse(BaseModel):
    enrollment_id: str
    course_id: str
    course_title: str | None = None
    course_code: str | None = None
    status: EnrollmentStatus
    enrolled_at: datetime
    target_completion_date: date | None = None
    completion_percentage: float = 0.0

    model_config = {"from_attributes": True}


class DeleteMessage(BaseModel):
    message: str
