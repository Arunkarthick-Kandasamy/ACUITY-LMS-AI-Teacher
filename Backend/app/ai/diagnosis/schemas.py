from __future__ import annotations

from pydantic import BaseModel, Field

from app.common.types import MisconceptionCategory


class DiagnosisResult(BaseModel):
    diagnosis_type: str = Field(
        description="misconception | knowledge_gap | minor_error | mastered"
    )
    misconception: str | None = Field(default=None, description="Description of detected misconception")
    misconception_category: MisconceptionCategory | None = Field(default=None)
    knowledge_gap: str | None = Field(default=None, description="Description of knowledge gap")
    prerequisite_concepts: list[str] = Field(default_factory=list)
    recommended_action: str = Field(
        description="reteach | prerequisite | example | continue"
    )
    evidence: list[str] = Field(default_factory=list)
    remediation: str | None = Field(default=None, description="Recommended next teaching action")
