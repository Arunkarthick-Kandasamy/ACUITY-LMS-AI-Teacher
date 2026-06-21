from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.teaching.models import Attempt, LessonProgress


class LessonProgressRepository(Repository[LessonProgress]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(LessonProgress, session)

    async def find_by_student_and_lesson(
        self, student_id: str, lesson_id: str
    ) -> LessonProgress | None:
        stmt = select(LessonProgress).where(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id == lesson_id,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_student(self, student_id: str) -> list[LessonProgress]:
        stmt = (
            select(LessonProgress)
            .where(LessonProgress.student_id == student_id)
            .order_by(LessonProgress.started_at.desc().nullsfirst())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class AttemptRepository(Repository[Attempt]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Attempt, session)

    async def find_by_student(
        self, student_id: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[Attempt], int]:
        return await self.find(
            Attempt.student_id == student_id,
            offset=offset,
            limit=limit,
            order_by=Attempt.attempted_at.desc(),
        )

    async def count_by_student(self, student_id: str) -> int:
        return await self.count(Attempt.student_id == student_id)
