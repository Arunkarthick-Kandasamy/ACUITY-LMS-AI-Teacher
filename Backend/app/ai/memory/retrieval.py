from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.memory.schemas import MemoryContext, MemoryObservation, MemoryQuery
from app.diagnosis.models import Misconception
from app.memory.models import MemoryEntry

logger = logging.getLogger(__name__)


class MemoryRetriever:
    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db
        self._qdrant_client: Any = None

    def _init_qdrant(self) -> Any:
        if self._qdrant_client is not None:
            return self._qdrant_client
        try:
            from qdrant_client import QdrantClient

            self._qdrant_client = QdrantClient(
                host="localhost",
                port=6333,
            )
        except ImportError:
            logger.warning("qdrant-client not available, using DB-only retrieval")
            self._qdrant_client = None
        except Exception as e:
            logger.warning("Qdrant connection failed: %s, using DB-only retrieval", e)
            self._qdrant_client = None
        return self._qdrant_client

    async def retrieve(self, query: MemoryQuery) -> MemoryContext:
        db_memories = await self._retrieve_from_db(query)
        semantic_memories = await self._retrieve_semantic(query)
        misconceptions = await self._retrieve_misconceptions(query)
        return MemoryContext(
            observations=db_memories,
            relevant_memories=[o.memory_text for o in db_memories],
            recurring_misconceptions=[m.memory_text for m in misconceptions],
            learning_signals=[o.memory_text for o in semantic_memories],
        )

    async def _retrieve_from_db(
        self, query: MemoryQuery
    ) -> list[MemoryObservation]:
        if self.db is None:
            return []
        stmt = (
            select(MemoryEntry)
            .where(
                MemoryEntry.student_id == query.student_id,
                MemoryEntry.is_active,
            )
            .order_by(MemoryEntry.confidence.desc())
            .limit(query.limit)
        )
        result = await self.db.execute(stmt)
        entries = result.unique().scalars().all()
        return [
            MemoryObservation(
                memory_key=e.memory_key,
                memory_text=e.memory_text,
                confidence=e.confidence,
                category=e.memory_key,
                evidence=[],
            )
            for e in entries
        ]

    async def _retrieve_semantic(
        self, query: MemoryQuery
    ) -> list[MemoryObservation]:
        qdrant = self._init_qdrant()
        if qdrant is None:
            return []
        try:
            results = qdrant.search(
                collection_name="student_memories",
                query_filter=self._build_qdrant_filter(query),
                limit=query.limit,
            )
            observations = []
            for hit in results:
                payload = hit.payload or {}
                observations.append(
                    MemoryObservation(
                        memory_key=payload.get("memory_key", "unknown"),
                        memory_text=payload.get("memory_text", ""),
                        confidence=hit.score,
                        category=payload.get("memory_key", "unknown"),
                        evidence=[],
                    )
                )
            return observations
        except Exception as e:
            logger.warning("Qdrant search failed: %s", e)
            return []

    async def _retrieve_misconceptions(
        self, query: MemoryQuery
    ) -> list[MemoryObservation]:
        if self.db is None:
            return []
        stmt = (
            select(Misconception)
            .where(
                Misconception.student_id == query.student_id,
                Misconception.is_resolved.is_(False),
            )
            .order_by(Misconception.frequency.desc())
            .limit(3)
        )
        result = await self.db.execute(stmt)
        misconceptions = result.unique().scalars().all()
        results: list[MemoryObservation] = []
        for m in misconceptions:
            cat = m.category.value if hasattr(m.category, "value") else m.category
            text = f"Recurring {cat} misconception: {m.description} (seen {m.frequency} times)"
            results.append(
                MemoryObservation(
                    memory_key="misconception_pattern",
                    memory_text=text,
                    confidence=min(0.5 + 0.1 * m.frequency, 0.95),
                    category="misconception",
                    evidence=m.evidence or [],
                )
            )
        return results

    def _build_qdrant_filter(self, query: MemoryQuery) -> Any:
        try:
            from qdrant_client.http.models import FieldCondition, Filter, MatchValue

            return Filter(
                must=[
                    FieldCondition(
                        key="student_id",
                        match=MatchValue(value=query.student_id),
                    ),
                ]
            )
        except ImportError:
            return None

    async def store_embedding(
        self, observation: MemoryObservation, student_id: str, session_id: str | None = None
    ) -> None:
        qdrant = self._init_qdrant()
        if qdrant is None:
            return
        try:
            qdrant.upsert(
                collection_name="student_memories",
                points=[
                    {
                        "id": hash(f"{student_id}:{observation.memory_key}:{observation.memory_text}"),
                        "vector": await self._generate_embedding(observation.memory_text),
                        "payload": {
                            "student_id": student_id,
                            "memory_key": observation.memory_key,
                            "memory_text": observation.memory_text,
                            "confidence": observation.confidence,
                            "source_session_id": session_id,
                            "category": observation.category,
                        },
                    }
                ],
            )
        except Exception as e:
            logger.warning("Qdrant upsert failed: %s", e)

    async def ensure_collection(self) -> None:
        qdrant = self._init_qdrant()
        if qdrant is None:
            return
        try:
            collections = qdrant.get_collections().collections
            existing = {c.name for c in collections}
            if "student_memories" not in existing:
                qdrant.create_collection(
                    collection_name="student_memories",
                    vectors_config={"size": 768, "distance": "Cosine"},
                )
                logger.info("Created qdrant collection: student_memories")
        except Exception as e:
            logger.warning("Qdrant collection setup failed: %s", e)

    async def _generate_embedding(self, text: str) -> list[float]:
        try:
            from app.ai.services.gemini import GeminiService

            gemini = GeminiService()
            result = await gemini.generate(
                f"Generate an embedding vector for: {text}",
                "You are an embedding generator. Return a list of 768 float values between -1 and 1.",
            )
            import json

            parsed = json.loads(result)
            if isinstance(parsed, list) and len(parsed) == 768:
                return parsed
        except Exception:
            pass
        return self._mock_embedding(text)

    def _mock_embedding(self, text: str) -> list[float]:
        import hashlib

        h = hashlib.sha256(text.encode()).digest()
        seed = int.from_bytes(h[:4], "little")
        rng = __import__("random").Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(768)]
