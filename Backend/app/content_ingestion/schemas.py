from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Job Status
# ---------------------------------------------------------------------------

class JobStatusResponse(BaseModel):
    upload_id: str
    filename: str
    file_type: str
    status: str
    error_message: str | None = None
    draft_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Draft
# ---------------------------------------------------------------------------

class ConceptContentItem(BaseModel):
    content_type: str
    content: str
    order_index: int


class ExerciseItem(BaseModel):
    question_type: str
    prompt: str
    options: dict | None = None
    correct_answer: str
    difficulty: float = 0.5
    order_index: int


class ExampleItem(BaseModel):
    content: str
    explanation: str | None = None
    order_index: int
    tags: list[str] = []


class ConceptItem(BaseModel):
    title: str
    description: str | None = None
    order_index: int
    estimated_duration_minutes: int = 15
    contents: list[ConceptContentItem] = []
    exercises: list[ExerciseItem] = []
    examples: list[ExampleItem] = []


class ObjectiveItem(BaseModel):
    code: str
    description: str
    order_index: int


class LessonItem(BaseModel):
    title: str
    order_index: int
    estimated_duration_minutes: int = 30
    is_required: bool = True
    concepts: list[ConceptItem] = []
    objectives: list[ObjectiveItem] = []


class ModuleItem(BaseModel):
    title: str
    description: str | None = None
    order_index: int
    estimated_duration_hours: int = 8
    lessons: list[LessonItem] = []


class KnowledgeGraphEdge(BaseModel):
    source_concept_title: str
    target_concept_title: str
    relationship: str = "requires"
    weight: float = 0.8


class CurriculumData(BaseModel):
    title: str
    description: str | None = None
    total_duration_hours: int = 40
    default_deadline_days: int = 90
    modules: list[ModuleItem] = []
    knowledge_graph: list[KnowledgeGraphEdge] = []


class DraftResponse(BaseModel):
    draft_id: str
    upload_id: str | None = None
    title: str
    status: str
    curriculum: CurriculumData | None = None
    course_id: str | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DraftListItem(BaseModel):
    draft_id: str
    title: str
    status: str
    course_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Approve / Publish
# ---------------------------------------------------------------------------

class ApproveResponse(BaseModel):
    draft_id: str
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublishResponse(BaseModel):
    draft_id: str
    status: str
    course_id: str
    course_title: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class ErrorMessage(BaseModel):
    message: str
