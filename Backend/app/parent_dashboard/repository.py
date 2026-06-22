from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.common.repository import Repository
from app.diagnosis.models import Misconception
from app.teaching.models import TeachingSession
from app.users.models import ParentStudentLink, StudentProfile


class ParentStudentLinkRepository(Repository[ParentStudentLink]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(ParentStudentLink, session)

    async def find_by_parent(self, parent_id: str) -> list[ParentStudentLink]:
        stmt = (
            select(ParentStudentLink)
            .where(ParentStudentLink.parent_id == parent_id)
            .options(joinedload(ParentStudentLink.student))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_parent_and_student(
        self, parent_id: str, student_id: str
    ) -> ParentStudentLink | None:
        stmt = select(ParentStudentLink).where(
            ParentStudentLink.parent_id == parent_id,
            ParentStudentLink.student_id == student_id,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class MisconceptionRepository(Repository[Misconception]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Misconception, session)

    async def find_by_student(self, student_id: str) -> list[Misconception]:
        stmt = (
            select(Misconception)
            .where(Misconception.student_id == student_id)
            .order_by(Misconception.detected_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_active_by_student(self, student_id: str) -> list[Misconception]:
        stmt = (
            select(Misconception)
            .where(
                Misconception.student_id == student_id,
                Misconception.is_resolved == False,  # noqa: E712
            )
            .order_by(Misconception.detected_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_knowledge_gaps(self, student_id: str) -> list[Misconception]:
        stmt = (
            select(Misconception)
            .where(
                Misconception.student_id == student_id,
                Misconception.category == "conceptual",
                Misconception.is_resolved == False,  # noqa: E712
            )
            .order_by(Misconception.detected_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class ParentTeachingSessionRepository(Repository[TeachingSession]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(TeachingSession, session)

    async def find_by_student(
        self, student_id: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[TeachingSession], int]:
        return await self.find(
            TeachingSession.student_id == student_id,
            offset=offset,
            limit=limit,
            order_by=TeachingSession.last_activity_at.desc(),
        )

    async def find_recent_by_student(
        self, student_id: str, days: int = 7
    ) -> list[TeachingSession]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(TeachingSession)
            .where(
                TeachingSession.student_id == student_id,
                TeachingSession.last_activity_at >= cutoff,
            )
            .order_by(TeachingSession.last_activity_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def count_by_student(self, student_id: str) -> int:
        return await self.count(TeachingSession.student_id == student_id)
