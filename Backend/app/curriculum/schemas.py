from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.common.types import ConceptContentType, LessonStatus, QuestionType

# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

class CourseCreate(BaseModel):
    code: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    description: str | None = None
    total_duration_hours: int = Field(..., ge=1)
    default_deadline_days: int = Field(..., ge=1)


class CourseUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    total_duration_hours: int | None = Field(None, ge=1)
    default_deadline_days: int | None = Field(None, ge=1)


class CourseResponse(BaseModel):
    course_id: str
    code: str
    title: str
    description: str | None
    total_duration_hours: int
    default_deadline_days: int
    is_published: bool
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CourseListResponse(BaseModel):
    course_id: str
    code: str
    title: str
    description: str | None
    total_duration_hours: int
    default_deadline_days: int
    is_published: bool
    module_count: int = 0
    lesson_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class CoursePublishRequest(BaseModel):
    is_published: bool


class CoursePublishResponse(BaseModel):
    course_id: str
    is_published: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeleteMessage(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------

class ModuleCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = None
    order_index: int = Field(..., ge=1)
    estimated_duration_hours: int | None = Field(None, gt=0)


class ModuleUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    order_index: int | None = Field(None, ge=1)
    estimated_duration_hours: int | None = Field(None, gt=0)


class ModuleResponse(BaseModel):
    module_id: str
    course_id: str
    title: str
    description: str | None
    order_index: int
    estimated_duration_hours: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ModuleListResponse(BaseModel):
    module_id: str
    title: str
    description: str | None
    order_index: int
    estimated_duration_hours: int | None
    lesson_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Lesson
# ---------------------------------------------------------------------------

class LessonCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content_url: str | None = None
    order_index: int = Field(..., ge=1)
    estimated_duration_minutes: int | None = Field(None, gt=0)
    is_required: bool = True
    status: LessonStatus = LessonStatus.DRAFT


class LessonUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    content_url: str | None = None
    order_index: int | None = Field(None, ge=1)
    estimated_duration_minutes: int | None = Field(None, gt=0)
    is_required: bool | None = None
    status: LessonStatus | None = None


class LessonResponse(BaseModel):
    lesson_id: str
    module_id: str
    title: str
    content_url: str | None
    order_index: int
    estimated_duration_minutes: int | None
    is_required: bool
    status: LessonStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class LessonListResponse(BaseModel):
    lesson_id: str
    title: str
    order_index: int
    estimated_duration_minutes: int | None
    status: LessonStatus
    concept_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Concept
# ---------------------------------------------------------------------------

class ConceptCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = None
    order_index: int = Field(..., ge=1)
    estimated_duration_minutes: int | None = Field(None, gt=0)


class ConceptUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    order_index: int | None = Field(None, ge=1)
    estimated_duration_minutes: int | None = Field(None, gt=0)


class ConceptResponse(BaseModel):
    concept_id: str
    lesson_id: str
    title: str
    description: str | None
    order_index: int
    estimated_duration_minutes: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConceptListResponse(BaseModel):
    concept_id: str
    title: str
    description: str | None
    order_index: int
    estimated_duration_minutes: int | None
    content_count: int = 0
    exercise_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ConceptContent
# ---------------------------------------------------------------------------

class ConceptContentCreate(BaseModel):
    content_type: ConceptContentType
    content: str
    order_index: int = Field(..., ge=0)


class ConceptContentUpdate(BaseModel):
    content: str | None = None
    order_index: int | None = Field(None, ge=0)
    content_type: ConceptContentType | None = None


class ConceptContentResponse(BaseModel):
    content_id: str
    concept_id: str
    content_type: ConceptContentType
    content: str
    order_index: int
    version: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ConceptContentListResponse(BaseModel):
    content_id: str
    content_type: ConceptContentType
    content: str
    order_index: int
    version: int
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------

class ExampleCreate(BaseModel):
    content: str
    explanation: str | None = None
    order_index: int = Field(..., ge=1)
    tags: list[str] | None = None


class ExampleUpdate(BaseModel):
    content: str | None = None
    explanation: str | None = None
    order_index: int | None = Field(None, ge=1)
    tags: list[str] | None = None


class ExampleResponse(BaseModel):
    example_id: str
    concept_id: str
    content: str
    explanation: str | None
    order_index: int
    tags: list[str] | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Exercise
# ---------------------------------------------------------------------------

class ExerciseCreate(BaseModel):
    question_type: QuestionType
    prompt: str
    options: dict | None = None
    correct_answer: str
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    order_index: int = Field(..., ge=1)
    tags: list[str] | None = None


class ExerciseUpdate(BaseModel):
    question_type: QuestionType | None = None
    prompt: str | None = None
    options: dict | None = None
    correct_answer: str | None = None
    difficulty: float | None = Field(None, ge=0.0, le=1.0)
    order_index: int | None = Field(None, ge=1)
    tags: list[str] | None = None


class ExerciseResponse(BaseModel):
    exercise_id: str
    concept_id: str
    question_type: QuestionType
    prompt: str
    options: dict | None
    correct_answer: str
    difficulty: float
    order_index: int
    tags: list[str] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExerciseListResponse(BaseModel):
    exercise_id: str
    question_type: QuestionType
    prompt: str
    difficulty: float
    order_index: int
    tags: list[str] | None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# LearningObjective
# ---------------------------------------------------------------------------

class LearningObjectiveCreate(BaseModel):
    code: str = Field(..., max_length=50)
    description: str
    success_criterion: dict | None = None
    order_index: int = Field(..., ge=1)


class LearningObjectiveUpdate(BaseModel):
    code: str | None = Field(None, max_length=50)
    description: str | None = None
    success_criterion: dict | None = None
    order_index: int | None = Field(None, ge=1)


class LearningObjectiveResponse(BaseModel):
    objective_id: str
    lesson_id: str
    code: str
    description: str
    success_criterion: dict | None
    order_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Lesson detail with concepts
# ---------------------------------------------------------------------------

class ConceptBrief(BaseModel):
    concept_id: str
    title: str
    description: str | None
    order_index: int
    estimated_duration_minutes: int | None

    model_config = {"from_attributes": True}


class LessonDetailResponse(BaseModel):
    lesson_id: str
    module_id: str
    title: str
    content_url: str | None
    order_index: int
    estimated_duration_minutes: int | None
    status: LessonStatus
    concepts: list[ConceptBrief]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Module detail with lessons
# ---------------------------------------------------------------------------

class LessonBrief(BaseModel):
    lesson_id: str
    title: str
    order_index: int
    estimated_duration_minutes: int | None
    concept_count: int = 0

    model_config = {"from_attributes": True}


class ModuleDetail(BaseModel):
    module_id: str
    title: str
    order_index: int
    lessons: list[LessonBrief]

    model_config = {"from_attributes": True}


class CourseDetailResponse(BaseModel):
    course_id: str
    code: str
    title: str
    description: str | None
    total_duration_hours: int
    default_deadline_days: int
    is_published: bool
    modules: list[ModuleDetail]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Concept detail with contents and examples
# ---------------------------------------------------------------------------

class ContentBrief(BaseModel):
    content_id: str
    content_type: ConceptContentType
    content: str
    order_index: int

    model_config = {"from_attributes": True}


class ExampleBrief(BaseModel):
    example_id: str
    content: str
    explanation: str | None

    model_config = {"from_attributes": True}


class ConceptDetailResponse(BaseModel):
    concept_id: str
    lesson_id: str
    title: str
    description: str | None
    order_index: int
    estimated_duration_minutes: int | None
    contents: list[ContentBrief]
    examples: list[ExampleBrief]
    exercise_count: int = 0

    model_config = {"from_attributes": True}
