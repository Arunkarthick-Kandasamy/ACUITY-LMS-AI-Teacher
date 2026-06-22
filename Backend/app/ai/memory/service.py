from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.memory.extraction import MemoryExtractor
from app.ai.memory.retrieval import MemoryRetriever
from app.ai.memory.schemas import MemoryContext, MemoryObservation, MemoryQuery
from app.memory.models import MemoryEntry

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db
        self.extractor = MemoryExtractor()
        self.retriever = MemoryRetriever(db)

    async def extract_and_store(
        self,
        student_id: str,
        session_id: str | None,
        concept_title: str,
        student_response: str,
        mastery_estimate: float,
        evaluation: str | None = None,
        diagnosis_type: str | None = None,
        misconception: str | None = None,
        misconception_category: str | None = None,
        knowledge_gap: str | None = None,
        recommended_action: str | None = None,
        evaluation_score: float | None = None,
    ) -> list[MemoryObservation]:
        observations = self.extractor.extract(
            concept_title=concept_title,
            student_response=student_response,
            mastery_estimate=mastery_estimate,
            evaluation=evaluation,
            diagnosis_type=diagnosis_type,
            misconception=misconception,
            misconception_category=misconception_category,
            knowledge_gap=knowledge_gap,
            recommended_action=recommended_action,
            evaluation_score=evaluation_score,
        )

        for obs in observations:
            await self._persist_observation(student_id, session_id, obs)
            await self.retriever.store_embedding(obs, student_id, session_id)

        return observations

    async def _persist_observation(
        self, student_id: str, session_id: str | None, obs: MemoryObservation
    ) -> MemoryEntry | None:
        if self.db is None:
            return None

        stmt = select(MemoryEntry).where(
            MemoryEntry.student_id == student_id,
            MemoryEntry.memory_key == obs.memory_key,
            MemoryEntry.memory_text == obs.memory_text,
        )
        result = await self.db.execute(stmt)
        existing = result.unique().scalar_one_or_none()

        if existing is not None:
            existing.confidence = max(existing.confidence, obs.confidence)
            return existing

        entry = MemoryEntry(
            student_id=student_id,
            memory_key=obs.memory_key,
            memory_text=obs.memory_text,
            confidence=obs.confidence,
            source_session_id=session_id,
        )
        self.db.add(entry)
        return entry

    async def retrieve_relevant(
        self, student_id: str, concept_id: str, lesson_id: str, limit: int = 5
    ) -> MemoryContext:
        query = MemoryQuery(
            student_id=student_id,
            concept_id=concept_id,
            lesson_id=lesson_id,
            limit=limit,
        )
        return await self.retriever.retrieve(query)

    async def format_memory_context(
        self, student_id: str, concept_id: str, lesson_id: str
    ) -> str:
        context = await self.retrieve_relevant(student_id, concept_id, lesson_id)
        parts = []
        if context.relevant_memories:
            parts.append("Student Memory Context:")
            for m in context.relevant_memories:
                parts.append(f"- {m}")
        if context.recurring_misconceptions:
            parts.append("Recurring Issues:")
            for m in context.recurring_misconceptions:
                parts.append(f"- {m}")
        if context.learning_signals:
            parts.append("Learning Signals:")
            for m in context.learning_signals:
                parts.append(f"- {m}")
        return "\n".join(parts) if parts else "No prior observations for this student."
