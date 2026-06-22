from __future__ import annotations

from pydantic import BaseModel


class MemoryObservation(BaseModel):
    memory_key: str
    memory_text: str
    confidence: float = 0.5
    category: str = "observation"
    evidence: list[str] = []


class MemoryContext(BaseModel):
    observations: list[MemoryObservation] = []
    relevant_memories: list[str] = []
    recurring_misconceptions: list[str] = []
    learning_signals: list[str] = []


class MemoryQuery(BaseModel):
    student_id: str
    concept_id: str
    lesson_id: str
    limit: int = 5
