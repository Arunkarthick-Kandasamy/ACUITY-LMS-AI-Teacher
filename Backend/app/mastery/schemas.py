from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MasteryResponse(BaseModel):
    record_id: str
    student_id: str
    concept_id: str
    concept_title: str | None = None
    mastery_level: float
    total_attempts: int
    consecutive_correct: int
    last_attempted_at: datetime | None = None

    model_config = {"from_attributes": True}


class MasterySummaryResponse(BaseModel):
    course_id: str
    total_concepts: int = 0
    mastered_concepts: int = 0
    average_mastery: float = 0.0
    concepts: list[MasteryResponse]

    model_config = {"from_attributes": True}
