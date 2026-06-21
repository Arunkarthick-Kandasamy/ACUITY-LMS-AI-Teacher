from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.common.types import SessionState
from app.teaching.models import TeachingSession


class TeachingSessionRepository(Repository[TeachingSession]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(TeachingSession, session)

    async def find_active_by_student_and_course(
        self, student_id: str, course_id: str
    ) -> TeachingSession | None:
        stmt = select(TeachingSession).where(
            TeachingSession.student_id == student_id,
            TeachingSession.course_id == course_id,
            TeachingSession.state == SessionState.ACTIVE,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_latest_resumable(
        self, student_id: str
    ) -> TeachingSession | None:
        stmt = (
            select(TeachingSession)
            .where(
                TeachingSession.student_id == student_id,
                TeachingSession.state.in_(
                    [SessionState.ACTIVE, SessionState.PAUSED]
                ),
            )
            .order_by(TeachingSession.last_activity_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_student(
        self, student_id: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[TeachingSession], int]:
        return await self.find(
            TeachingSession.student_id == student_id,
            offset=offset,
            limit=limit,
            order_by=TeachingSession.started_at.desc(),
        )
