from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    title: str
    description: str | None = None
    lesson_id: str | None = None
    module_id: str | None = None
    course_id: str
    assessment_type: str
    passing_score: float = 0.7
    time_limit: int | None = None
    max_attempts: int = 1
    is_published: bool = False


class AssessmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    lesson_id: str | None = None
    module_id: str | None = None
    assessment_type: str | None = None
    passing_score: float | None = None
    time_limit: int | None = None
    max_attempts: int | None = None
    is_published: bool | None = None


class AssessmentResponse(BaseModel):
    id: str
    title: str
    description: str | None
    lesson_id: str | None
    module_id: str | None
    course_id: str
    assessment_type: str
    passing_score: float
    time_limit: int | None
    max_attempts: int
    is_published: bool
    created_by: str
    question_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssessmentDetail(BaseModel):
    id: str
    title: str
    description: str | None
    lesson_id: str | None
    module_id: str | None
    course_id: str
    assessment_type: str
    passing_score: float
    time_limit: int | None
    max_attempts: int
    is_published: bool
    question_count: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class QuestionCreate(BaseModel):
    assessment_id: str
    question_type: str
    prompt: str
    options: dict[str, Any] | None = None
    correct_answer: str
    difficulty: float = 0.5
    marks: float = 1.0
    explanation: str | None = None
    order_index: int = 0


class QuestionUpdate(BaseModel):
    question_type: str | None = None
    prompt: str | None = None
    options: dict[str, Any] | None = None
    correct_answer: str | None = None
    difficulty: float | None = None
    marks: float | None = None
    explanation: str | None = None
    order_index: int | None = None


class QuestionResponse(BaseModel):
    id: str
    assessment_id: str
    question_type: str
    prompt: str
    options: dict[str, Any] | None
    difficulty: float
    marks: float
    explanation: str | None
    order_index: int
    created_at: datetime | None = None


class QuestionPublic(BaseModel):
    id: str
    question_type: str
    prompt: str
    options: dict[str, Any] | None
    difficulty: float
    marks: float
    order_index: int


class AttemptStartResponse(BaseModel):
    attempt_id: str
    assessment_id: str
    started_at: datetime
    attempt_number: int
    questions: list[QuestionPublic]
    time_limit: int | None = None
    time_limit_seconds: int | None = None


class SubmitRequest(BaseModel):
    responses: list[QuestionAnswer]


class QuestionAnswer(BaseModel):
    question_id: str
    response: str
    time_taken_seconds: int | None = None


class SubmitResponse(BaseModel):
    attempt_id: str
    assessment_id: str
    score: float
    percentage: float
    passed: bool
    total_marks: float
    earned_marks: float
    completed_at: datetime


class AttemptResultResponse(BaseModel):
    attempt_id: str
    assessment_id: str
    assessment_title: str
    assessment_type: str
    passing_score: float
    score: float
    percentage: float
    passed: bool
    attempt_number: int
    started_at: datetime | None
    completed_at: datetime | None
    total_marks: float
    earned_marks: float
    responses: list[ResponseDetail]


class ResponseDetail(BaseModel):
    question_id: str
    prompt: str
    question_type: str
    marks: float
    response: str
    correct_answer: str
    is_correct: bool
    score: float
    feedback: str | None
    explanation: str | None


class AttemptHistoryItem(BaseModel):
    attempt_id: str
    assessment_id: str
    assessment_title: str = ""
    assessment_type: str = ""
    score: float
    percentage: float
    passed: bool
    attempt_number: int
    started_at: datetime | None
    completed_at: datetime | None


class QuestionBankCreate(BaseModel):
    course_id: str
    lesson_id: str | None = None
    concept_id: str | None = None
    question_type: str
    prompt: str
    options: dict[str, Any] | None = None
    correct_answer: str
    difficulty: float = 0.5
    marks: float = 1.0
    explanation: str | None = None
    tags: list[str] | None = None


class QuestionBankResponse(BaseModel):
    id: str
    course_id: str
    lesson_id: str | None
    concept_id: str | None
    question_type: str
    prompt: str
    options: dict[str, Any] | None
    difficulty: float
    marks: float
    explanation: str | None
    tags: list[str] | None
    created_at: datetime | None
    updated_at: datetime | None
