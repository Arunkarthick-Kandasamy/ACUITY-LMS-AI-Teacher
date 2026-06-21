from __future__ import annotations

from sqlalchemy import func, select

from app.common.repository import Repository
from app.curriculum.models import (
    Concept,
    ConceptContent,
    Course,
    Example,
    Exercise,
    LearningObjective,
    Lesson,
    Module,
)


class CourseRepository(Repository[Course]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Course, session)

    async def get_by_code(self, code: str) -> Course | None:
        stmt = select(Course).where(Course.code == code)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_paginated(
        self,
        is_published: bool | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Course], int]:
        conditions = []
        if is_published is not None:
            conditions.append(Course.is_published == is_published)
        if search:
            like = f"%{search}%"
            conditions.append(Course.title.ilike(like) | Course.code.ilike(like))
        return await self.find(*conditions, offset=offset, limit=limit, order_by=Course.created_at.desc())


class ModuleRepository(Repository[Module]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Module, session)

    async def get_max_order(self, course_id: str) -> int:
        stmt = select(func.max(Module.order_index)).where(Module.course_id == course_id)
        return await self.session.scalar(stmt) or 0

    async def find_by_course(self, course_id: str) -> list[Module]:
        stmt = select(Module).where(Module.course_id == course_id).order_by(Module.order_index)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class LessonRepository(Repository[Lesson]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Lesson, session)

    async def get_max_order(self, module_id: str) -> int:
        stmt = select(func.max(Lesson.order_index)).where(Lesson.module_id == module_id)
        return await self.session.scalar(stmt) or 0

    async def find_by_module(self, module_id: str) -> list[Lesson]:
        stmt = select(Lesson).where(Lesson.module_id == module_id).order_by(Lesson.order_index)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class ConceptRepository(Repository[Concept]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Concept, session)

    async def get_max_order(self, lesson_id: str) -> int:
        stmt = select(func.max(Concept.order_index)).where(Concept.lesson_id == lesson_id)
        return await self.session.scalar(stmt) or 0

    async def find_by_lesson(self, lesson_id: str) -> list[Concept]:
        stmt = select(Concept).where(Concept.lesson_id == lesson_id).order_by(Concept.order_index)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def count_by_lesson(self, lesson_id: str) -> int:
        stmt = select(func.count()).select_from(Concept).where(Concept.lesson_id == lesson_id)
        return await self.session.scalar(stmt) or 0


class ConceptContentRepository(Repository[ConceptContent]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(ConceptContent, session)

    async def get_max_order(self, concept_id: str) -> int:
        stmt = select(func.max(ConceptContent.order_index)).where(ConceptContent.concept_id == concept_id)
        return await self.session.scalar(stmt) or 0

    async def find_by_concept(self, concept_id: str) -> list[ConceptContent]:
        stmt = (
            select(ConceptContent)
            .where(ConceptContent.concept_id == concept_id)
            .order_by(ConceptContent.order_index)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class ExampleRepository(Repository[Example]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Example, session)

    async def get_max_order(self, concept_id: str) -> int:
        stmt = select(func.max(Example.order_index)).where(Example.concept_id == concept_id)
        return await self.session.scalar(stmt) or 0

    async def find_by_concept(self, concept_id: str) -> list[Example]:
        stmt = select(Example).where(Example.concept_id == concept_id).order_by(Example.order_index)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class ExerciseRepository(Repository[Exercise]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Exercise, session)

    async def get_max_order(self, concept_id: str) -> int:
        stmt = select(func.max(Exercise.order_index)).where(Exercise.concept_id == concept_id)
        return await self.session.scalar(stmt) or 0

    async def find_by_concept(self, concept_id: str) -> list[Exercise]:
        stmt = select(Exercise).where(Exercise.concept_id == concept_id).order_by(Exercise.order_index)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class LearningObjectiveRepository(Repository[LearningObjective]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(LearningObjective, session)

    async def get_max_order(self, lesson_id: str) -> int:
        stmt = select(func.max(LearningObjective.order_index)).where(LearningObjective.lesson_id == lesson_id)
        return await self.session.scalar(stmt) or 0

    async def find_by_lesson(self, lesson_id: str) -> list[LearningObjective]:
        stmt = (
            select(LearningObjective)
            .where(LearningObjective.lesson_id == lesson_id)
            .order_by(LearningObjective.order_index)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
