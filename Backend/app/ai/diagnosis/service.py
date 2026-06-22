from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.diagnosis.prompts import PROMPT_DIAGNOSE, SYSTEM_DIAGNOSE
from app.ai.diagnosis.schemas import DiagnosisResult
from app.ai.services.gemini import GeminiService
from app.common.types import MisconceptionCategory
from app.diagnosis.models import Misconception


class DiagnosisService:
    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db
        self.gemini = GeminiService()

    async def diagnose(
        self,
        concept_title: str,
        concept_description: str,
        teaching_content: str,
        question: str,
        student_response: str,
        mastery_estimate: float,
        prerequisite_concepts: list[dict] | None = None,
        conversation_history: str | None = None,
    ) -> DiagnosisResult:
        prereq_text = _format_prerequisites(prerequisite_concepts or [])

        prompt = PROMPT_DIAGNOSE.format(
            concept_title=concept_title,
            concept_description=concept_description,
            teaching_content=teaching_content,
            question=question,
            expected_answer="See concept content for expected knowledge",
            student_response=student_response or "",
            mastery_estimate=mastery_estimate,
            prerequisite_concepts=prereq_text,
            conversation_history=conversation_history or "No previous conversation.",
        )

        raw = await self.gemini.generate_json(prompt, SYSTEM_DIAGNOSE)

        return DiagnosisResult(
            diagnosis_type=raw.get("diagnosis_type", "minor_error"),
            misconception=raw.get("misconception"),
            misconception_category=_parse_category(raw.get("misconception_category")),
            knowledge_gap=raw.get("knowledge_gap"),
            prerequisite_concepts=raw.get("prerequisite_concepts", []),
            recommended_action=raw.get("recommended_action", "example"),
            evidence=raw.get("evidence", []),
            remediation=raw.get("remediation"),
        )

    async def persist_misconception(
        self,
        student_id: str,
        concept_id: str,
        category: MisconceptionCategory,
        description: str,
        session_id: str | None = None,
        evidence: list[str] | None = None,
    ) -> Misconception | None:
        if self.db is None:
            return None

        from sqlalchemy import select

        stmt = select(Misconception).where(
            Misconception.student_id == student_id,
            Misconception.concept_id == concept_id,
            Misconception.category == category,
            Misconception.is_resolved == False,  # noqa: E712
        )
        result = await self.db.execute(stmt)
        existing = result.unique().scalar_one_or_none()

        if existing is not None:
            existing.frequency += 1
            if evidence:
                current = list(existing.evidence or [])
                current.extend(evidence)
                existing.evidence = current
            await self.db.flush()
            await self.db.refresh(existing)
            return existing

        misconception = Misconception(
            student_id=student_id,
            concept_id=concept_id,
            category=category,
            description=description,
            detected_in_session_id=session_id,
            evidence=evidence or [],
            frequency=1,
            is_resolved=False,
            detected_at=datetime.now(timezone.utc),
        )
        self.db.add(misconception)
        await self.db.flush()
        await self.db.refresh(misconception)
        return misconception


def _parse_category(raw: str | None) -> MisconceptionCategory | None:
    if raw is None:
        return None
    try:
        return MisconceptionCategory(raw.lower())
    except ValueError:
        return None


def _format_prerequisites(concepts: list[dict]) -> str:
    if not concepts:
        return "None identified"
    lines = []
    for c in concepts:
        title = c.get("title", c.get("label", "Unknown"))
        rel = c.get("relationship", "requires")
        lines.append(f"- {title} ({rel})")
    return "\n".join(lines)
