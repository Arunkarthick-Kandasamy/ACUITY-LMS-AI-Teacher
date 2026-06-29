from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.gamification.models import Badge, Streak, UserAchievement
from app.gamification.repository import AchievementRepository, BadgeRepository, StreakRepository
from app.gamification.schemas import AchievementResponse, BadgeResponse, StreakResponse
from app.users.models import User


class GamificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.badge_repo = BadgeRepository(session)
        self.ach_repo = AchievementRepository(session)
        self.streak_repo = StreakRepository(session)

    async def create_badge(self, name: str, description: str | None, icon_url: str | None, category: str, criteria: str | None) -> BadgeResponse:
        badge = Badge(name=name, description=description, icon_url=icon_url, category=category, criteria=criteria)
        self.session.add(badge)
        await self.session.flush()
        return BadgeResponse.model_validate(badge)

    async def list_badges(self) -> list[BadgeResponse]:
        badges = await self.badge_repo.list()
        return [BadgeResponse.model_validate(b) for b in badges]

    async def award_badge(self, user: User, badge_id: str) -> AchievementResponse:
        badge = await self.badge_repo.get(badge_id)
        if badge is None:
            raise NotFoundException(message="Badge not found")
        existing = await self.ach_repo.find_by_user_and_badge(user.id, badge_id)
        if existing:
            raise NotFoundException(message="Badge already awarded")
        ach = UserAchievement(user_id=user.id, badge_id=badge_id)
        self.session.add(ach)
        await self.session.flush()
        resp = AchievementResponse.model_validate(ach)
        resp.badge_name = badge.name
        resp.badge_icon_url = badge.icon_url
        resp.badge_category = badge.category
        return resp

    async def get_achievements(self, user: User) -> list[AchievementResponse]:
        achievements = await self.ach_repo.find_by_user(user.id)
        result = []
        for ach in achievements:
            badge = await self.badge_repo.get(ach.badge_id)
            resp = AchievementResponse.model_validate(ach)
            if badge:
                resp.badge_name = badge.name
                resp.badge_icon_url = badge.icon_url
                resp.badge_category = badge.category
            result.append(resp)
        return result

    async def record_activity(self, user: User) -> StreakResponse:
        streak = await self.streak_repo.find_by_user(user.id)
        if streak is None:
            streak = Streak(user_id=user.id, current_streak=1, longest_streak=1, last_activity_date=datetime.now(timezone.utc))
            self.session.add(streak)
        else:
            today = date.today()
            last = streak.last_activity_date.date() if streak.last_activity_date else None
            if last != today:
                if last == date.fromordinal(today.toordinal() - 1):
                    streak.current_streak += 1
                else:
                    streak.current_streak = 1
                streak.longest_streak = max(streak.longest_streak, streak.current_streak)
                streak.last_activity_date = datetime.now(timezone.utc)
        await self.session.flush()
        return StreakResponse.model_validate(streak)

    async def get_streak(self, user: User) -> StreakResponse:
        streak = await self.streak_repo.find_by_user(user.id)
        if streak is None:
            return StreakResponse(user_id=user.id, current_streak=0, longest_streak=0)
        return StreakResponse.model_validate(streak)
