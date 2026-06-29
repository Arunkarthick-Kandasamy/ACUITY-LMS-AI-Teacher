from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.gamification.schemas import AwardBadgeRequest, BadgeCreate
from app.gamification.service import GamificationService
from app.infrastructure.database import get_session
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/gamification", tags=["Gamification"])


@router.post("/badges")
async def create_badge(
    body: BadgeCreate,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = GamificationService(session)
    badge = await svc.create_badge(body.name, body.description, body.icon_url, body.category, body.criteria)
    return success_response(badge.model_dump(mode="json"))


@router.get("/badges")
async def list_badges(
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = GamificationService(session)
    badges = await svc.list_badges()
    return success_response([b.model_dump(mode="json") for b in badges])


@router.post("/award/{user_id}")
async def award_badge_to_user(
    user_id: str,
    body: AwardBadgeRequest,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    """Admin awards a badge to a user"""
    from app.users.repository import UserRepository
    user_repo = UserRepository(session)
    user = await user_repo.get(user_id)
    if user is None:
        from app.common.exceptions import NotFoundException
        raise NotFoundException(message="User not found")
    svc = GamificationService(session)
    result = await svc.award_badge(user, body.badge_id)
    return success_response(result.model_dump(mode="json"))


@router.get("/achievements/me")
async def my_achievements(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    svc = GamificationService(session)
    achievements = await svc.get_achievements(current_user)
    return success_response([a.model_dump(mode="json") for a in achievements])


@router.post("/activity")
async def record_activity(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    svc = GamificationService(session)
    streak = await svc.record_activity(current_user)
    return success_response(streak.model_dump(mode="json"))


@router.get("/streak/me")
async def my_streak(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    svc = GamificationService(session)
    streak = await svc.get_streak(current_user)
    return success_response(streak.model_dump(mode="json"))
