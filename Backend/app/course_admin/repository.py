from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.course_admin.models import Course, KnowledgeSource, PipelineStage, StageStatus


class CourseRepository(Repository[Course]):
    def __init__(self, session) -> None:
        super().__init__(Course, session)

    async def find_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[Course]:
        stmt = (
            select(Course)
            .where(Course.user_id == user_id)
            .order_by(Course.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class PipelineStageRepository(Repository[PipelineStage]):
    def __init__(self, session) -> None:
        super().__init__(PipelineStage, session)

    async def find_by_course(self, course_id: str) -> list[PipelineStage]:
        stmt = (
            select(PipelineStage)
            .where(PipelineStage.course_id == course_id)
            .order_by(PipelineStage.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_stage(
        self, course_id: str, stage_name: str
    ) -> PipelineStage | None:
        stmt = select(PipelineStage).where(
            PipelineStage.course_id == course_id,
            PipelineStage.stage_name == stage_name,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_next_pending_stage(
        self, course_id: str
    ) -> PipelineStage | None:
        stmt = (
            select(PipelineStage)
            .where(
                PipelineStage.course_id == course_id,
                PipelineStage.status == StageStatus.PENDING,
            )
            .order_by(PipelineStage.created_at)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class KnowledgeSourceRepository(Repository[KnowledgeSource]):
    def __init__(self, session) -> None:
        super().__init__(KnowledgeSource, session)

    async def find_by_course(self, course_id: str) -> list[KnowledgeSource]:
        stmt = (
            select(KnowledgeSource)
            .where(KnowledgeSource.course_id == course_id)
            .order_by(KnowledgeSource.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
