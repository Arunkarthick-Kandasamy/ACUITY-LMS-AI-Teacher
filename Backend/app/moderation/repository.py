from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.moderation.models import ModerationQueue


class ModerationRepository(Repository[ModerationQueue]):
    def __init__(self, session) -> None:
        super().__init__(ModerationQueue, session)

    async def find_pending(self, limit: int = 50, offset: int = 0) -> list[ModerationQueue]:
        stmt = (
            select(ModerationQueue)
            .where(ModerationQueue.status == "pending")
            .order_by(ModerationQueue.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_status(self, status: str, limit: int = 50, offset: int = 0) -> list[ModerationQueue]:
        stmt = (
            select(ModerationQueue)
            .where(ModerationQueue.status == status)
            .order_by(ModerationQueue.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
