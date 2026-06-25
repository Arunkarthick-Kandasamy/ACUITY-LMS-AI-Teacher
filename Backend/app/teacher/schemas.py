from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TeacherStudentResponse(BaseModel):
    student_id: str
    full_name: str
    email: str
    grade_level: str | None = None
    active_courses: int = 0
    overall_mastery_avg: float = 0.0
    last_active: datetime | None = None
    current_streak_days: int = 0
    assigned_at: datetime | None = None


class TeacherCourseResponse(BaseModel):
    course_id: str
    title: str
    code: str
    role: str
    assigned_at: datetime | None = None


class MasteryConceptItem(BaseModel):
    concept_id: str
    concept_title: str | None = None
    mastery_level: float
    total_attempts: int
    consecutive_correct: int
    last_attempted_at: datetime | None = None


class MasterySummaryResponse(BaseModel):
    total_concepts: int
    mastered_concepts: int
    in_progress_concepts: int
    not_started_concepts: int
    average_mastery: float
    concepts: list[MasteryConceptItem]


class ProgressSummaryResponse(BaseModel):
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    completion_percentage: float


class SessionItem(BaseModel):
    session_id: str
    course_id: str
    course_title: str | None = None
    state: str
    started_at: datetime | None = None
    last_activity_at: datetime | None = None


class AttemptItem(BaseModel):
    attempt_id: str
    exercise_id: str
    is_correct: bool
    score: float
    attempted_at: datetime | None = None
    concept_title: str | None = None


class MisconceptionItem(BaseModel):
    misconception_id: str
    concept_id: str
    concept_title: str | None = None
    category: str
    description: str
    detected_at: datetime | None = None
    frequency: int
    is_resolved: bool


class TeacherDashboardResponse(BaseModel):
    total_students: int
    total_courses: int
    students: list[TeacherStudentResponse]
    recent_sessions: list[SessionItem]
