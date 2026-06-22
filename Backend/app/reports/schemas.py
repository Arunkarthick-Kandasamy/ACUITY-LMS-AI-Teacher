from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class StrengthItem(BaseModel):
    description: str
    category: str = "academic"
    evidence: list[str] = []


class ChallengeItem(BaseModel):
    description: str
    category: str = "conceptual"
    severity: str = "medium"
    concept_title: str | None = None


class RecommendationItem(BaseModel):
    description: str
    priority: str = "medium"
    category: str = "practice"


class RiskIndicator(BaseModel):
    risk_type: str
    description: str
    severity: str = "medium"
    actionable: bool = True


class ReportData(BaseModel):
    title: str
    executive_summary: str
    strengths: list[StrengthItem] = []
    challenges: list[ChallengeItem] = []
    recommendations: list[RecommendationItem] = []
    risk_indicators: list[RiskIndicator] = []


class ReportResponse(BaseModel):
    id: str
    student_id: str
    parent_id: str | None = None
    report_type: str
    title: str | None = None
    generated_at: datetime | None = None
    summary: str | None = None
    recommendations: list[Any] = []
    report_data: ReportData | None = None
    is_read: bool = False
    created_at: datetime | None = None


class ReportListItem(BaseModel):
    id: str
    student_id: str
    report_type: str
    title: str | None = None
    generated_at: datetime | None = None
    summary: str | None = None
    is_read: bool = False
    created_at: datetime | None = None
