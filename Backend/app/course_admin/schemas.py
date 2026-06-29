from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StageLogEntry(BaseModel):
    ts: str
    message: str
    level: str = "info"

    model_config = {"from_attributes": True}


class PipelineStageResponse(BaseModel):
    id: str
    stage_name: str
    status: str
    progress_pct: int = 0
    error_message: str | None = None
    output_data: dict | None = None
    stage_logs: list[StageLogEntry] = []
    retry_count: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeSourceResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class StageProgress(BaseModel):
    completed: int
    total: int
    pct: float

    model_config = {"from_attributes": True}


class CourseBriefResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    status: str
    course_id: str | None = None
    stage_progress: StageProgress | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CourseDetailResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    status: str
    course_id: str | None = None
    stage_progress: StageProgress | None = None
    knowledge_sources: list[KnowledgeSourceResponse] = []
    knowledge_graph_data: dict | None = None
    teaching_profile: dict | None = None
    course_structure: dict | None = None
    simulation_results: dict | None = None
    error_message: str | None = None
    stages: list[PipelineStageResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateCourseRequest(BaseModel):
    name: str
    description: str | None = None


class UpdateKnowledgeGraphRequest(BaseModel):
    knowledge_graph_data: dict


class UpdateTeachingProfileRequest(BaseModel):
    teaching_profile: dict


class UpdateCourseStructureRequest(BaseModel):
    course_structure: dict


class DashboardStats(BaseModel):
    total_courses: int = 0
    deployed_count: int = 0
    training_count: int = 0
    draft_count: int = 0
    review_count: int = 0
    total_students: int = 0
    total_published: int = 0
    active_sessions: int = 0
    pending_review_count: int = 0
    failed_stages_count: int = 0
    total_concepts_generated: int = 0
    total_exercises_generated: int = 0
    avg_coverage_pct: float = 0
    recent_courses: list[CourseBriefResponse] = []
