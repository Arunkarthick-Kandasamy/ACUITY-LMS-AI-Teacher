from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.database import get_session
from app.moderation.schemas import ReviewRequest
from app.moderation.service import ModerationService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/moderation", tags=["Moderation"])


@router.get("/queue")
async def list_queue(
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = ModerationService(session)
    items = await service.list_queue(status)
    return success_response([i.model_dump(mode="json") for i in items])


@router.post("/queue/{item_id}/review")
async def review_item(
    item_id: str,
    body: ReviewRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = ModerationService(session)
    item = await service.review(item_id, current_user, body.status, body.review_notes)
    return success_response(item.model_dump(mode="json"))
