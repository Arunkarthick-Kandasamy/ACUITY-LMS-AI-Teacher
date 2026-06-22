from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


class ParentStudentResponse(BaseModel):
    student_id: str
    full_name: str
    grade_level: str | None = None
    current_streak_days: int = 0


class StudentProfileResponse(BaseModel):
    student_id: str
    full_name: str
    email: str
    grade_level: str | None = None
    current_streak_days: int = 0
    avg_session_duration_minutes: int = 0
    created_at: datetime | None = None


class ProgressSummaryResponse(BaseModel):
    total_lessons: int = 0
    completed_lessons: int = 0
    in_progress_lessons: int = 0
    not_started_lessons: int = 0
    completion_percentage: float = 0.0


class CurriculumNode(BaseModel):
    module_id: str
    module_title: str
    module_order: int
    lessons: list[dict[str, Any]] = []


class CurriculumTreeResponse(BaseModel):
    course_id: str
    course_title: str
    modules: list[CurriculumNode] = []


class MasteryConceptResponse(BaseModel):
    concept_id: str
    concept_title: str | None = None
    lesson_title: str | None = None
    mastery_level: float = 0.0
    total_attempts: int = 0
    consecutive_correct: int = 0
    last_attempted_at: datetime | None = None


class MasterySummaryResponse(BaseModel):
    total_concepts: int = 0
    mastered_concepts: int = 0
    in_progress_concepts: int = 0
    not_started_concepts: int = 0
    average_mastery: float = 0.0
    concepts: list[MasteryConceptResponse] = []


class PacingStatusResponse(BaseModel):
    enrollment_id: str
    course_id: str
    course_title: str | None = None
    current_week: int = 1
    target_lessons_per_week: int = 3
    pace_status: str = "on_track"
    last_pacing_adjustment_at: datetime | None = None


class MisconceptionResponse(BaseModel):
    misconception_id: str
    concept_id: str
    concept_title: str | None = None
    category: str | None = None
    description: str
    detected_at: datetime | None = None
    frequency: int = 1
    is_resolved: bool = False
    resolved_at: datetime | None = None


class KnowledgeGapResponse(BaseModel):
    gap_id: str
    concept_id: str
    concept_title: str | None = None
    description: str
    detected_at: datetime | None = None
    frequency: int = 1


class TeachingSessionResponse(BaseModel):
    session_id: str
    course_id: str
    course_title: str | None = None
    concept_title: str | None = None
    state: str
    started_at: datetime | None = None
    last_activity_at: datetime | None = None
    completed_at: datetime | None = None


class RecentActivityItem(BaseModel):
    activity_type: str
    description: str
    timestamp: datetime | None = None
    session_id: str | None = None
    concept_title: str | None = None


class DashboardResponse(BaseModel):
    student: StudentProfileResponse
    progress: ProgressSummaryResponse
    mastery: MasterySummaryResponse
    active_misconceptions: list[MisconceptionResponse] = []
    knowledge_gaps: list[KnowledgeGapResponse] = []
    pacing: list[PacingStatusResponse] = []
    recent_sessions: list[TeachingSessionResponse] = []
    recent_activity: list[RecentActivityItem] = []
    learning_streak_days: int = 0
    completion_forecast: dict[str, Any] = {}
