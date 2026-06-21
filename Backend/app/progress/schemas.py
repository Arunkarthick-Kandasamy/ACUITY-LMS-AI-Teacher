from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.common.types import LessonProgressStatus, QuestionType


class LessonProgressUpdate(BaseModel):
    status: LessonProgressStatus | None = None
    time_spent_seconds: int | None = Field(None, ge=0)
    completion_percentage: float | None = Field(None, ge=0.0, le=100.0)


class LessonProgressResponse(BaseModel):
    progress_id: str
    student_id: str
    lesson_id: str
    status: LessonProgressStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    time_spent_seconds: int = 0
    completion_percentage: float = 0.0

    model_config = {"from_attributes": True}


class CurriculumModule(BaseModel):
    module_id: str
    title: str
    order_index: int
    lesson_count: int = 0


class CurriculumLesson(BaseModel):
    lesson_id: str
    title: str
    order_index: int
    status: str | None = None
    estimated_duration_minutes: int | None = None


class CurriculumTreeResponse(BaseModel):
    course_id: str
    course_title: str
    course_code: str
    modules: list[CurriculumModule]

    model_config = {"from_attributes": True}


class AttemptCreate(BaseModel):
    exercise_id: str
    response: str
    is_correct: bool
    score: float | None = Field(None, ge=0.0, le=1.0)
    time_taken_seconds: int | None = Field(None, ge=0)
    teaching_session_id: str | None = None
    ai_feedback: str | None = None


class AttemptResponse(BaseModel):
    attempt_id: str
    exercise_id: str
    student_id: str
    response: str
    is_correct: bool
    score: float | None = None
    time_taken_seconds: int | None = None
    attempt_number: int
    attempted_at: datetime
    ai_feedback: str | None = None

    model_config = {"from_attributes": True}


class AttemptHistoryItem(BaseModel):
    attempt_id: str
    exercise_id: str
    question_type: QuestionType | None = None
    prompt: str | None = None
    is_correct: bool
    score: float | None = None
    attempt_number: int
    attempted_at: datetime

    model_config = {"from_attributes": True}
