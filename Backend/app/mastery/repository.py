from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.mastery.models import MasteryRecord


class MasteryRecordRepository(Repository[MasteryRecord]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(MasteryRecord, session)

    async def find_by_student(self, student_id: str) -> list[MasteryRecord]:
        stmt = (
            select(MasteryRecord)
            .where(MasteryRecord.student_id == student_id)
            .order_by(MasteryRecord.mastery_level.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_student_and_concept(
        self, student_id: str, concept_id: str
    ) -> MasteryRecord | None:
        stmt = select(MasteryRecord).where(
            MasteryRecord.student_id == student_id,
            MasteryRecord.concept_id == concept_id,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_student_and_course(
        self, student_id: str, course_id: str
    ) -> list[MasteryRecord]:
        from app.curriculum.models import Concept, Lesson, Module

        stmt = (
            select(MasteryRecord)
            .join(Concept, MasteryRecord.concept_id == Concept.id)
            .join(Lesson, Concept.lesson_id == Lesson.id)
            .join(Module, Lesson.module_id == Module.id)
            .where(Module.course_id == course_id, MasteryRecord.student_id == student_id)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
