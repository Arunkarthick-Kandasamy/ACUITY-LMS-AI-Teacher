from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.gamification.models import Badge, Streak, UserAchievement


class BadgeRepository(Repository[Badge]):
    def __init__(self, session) -> None:
        super().__init__(Badge, session)


class AchievementRepository(Repository[UserAchievement]):
    def __init__(self, session) -> None:
        super().__init__(UserAchievement, session)

    async def find_by_user(self, user_id: str) -> list[UserAchievement]:
        stmt = select(UserAchievement).where(UserAchievement.user_id == user_id).order_by(UserAchievement.earned_at.desc())
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_user_and_badge(self, user_id: str, badge_id: str) -> UserAchievement | None:
        stmt = select(UserAchievement).where(UserAchievement.user_id == user_id, UserAchievement.badge_id == badge_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class StreakRepository(Repository[Streak]):
    def __init__(self, session) -> None:
        super().__init__(Streak, session)

    async def find_by_user(self, user_id: str) -> Streak | None:
        stmt = select(Streak).where(Streak.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
