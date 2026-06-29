from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.moderation.models import ModerationQueue
from app.moderation.repository import ModerationRepository
from app.moderation.schemas import ModerationItemResponse
from app.users.models import User
from app.users.repository import UserRepository


class ModerationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ModerationRepository(session)
        self.user_repo = UserRepository(session)

    async def add_to_queue(self, content_id: str, content_type: str, uploader_id: str, flag_reason: str | None = None) -> ModerationQueue:
        item = ModerationQueue(
            content_id=content_id,
            content_type=content_type,
            uploader_id=uploader_id,
            flag_reason=flag_reason,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def list_queue(self, status: str | None = None) -> list[ModerationItemResponse]:
        items = await self.repo.find_pending() if status is None else await self.repo.find_by_status(status)
        result = []
        for item in items:
            uploader = await self.user_repo.get(item.uploader_id)
            resp = ModerationItemResponse.model_validate(item)
            resp.uploader_name = uploader.full_name if uploader else "Unknown"
            result.append(resp)
        return result

    async def review(self, item_id: str, reviewer: User, status: str, review_notes: str | None = None) -> ModerationItemResponse:
        item = await self.repo.get(item_id)
        if item is None:
            raise NotFoundException(message="Moderation item not found")
        item.status = status
        item.reviewer_id = reviewer.id
        item.review_notes = review_notes
        item.reviewed_at = datetime.now(timezone.utc)
        await self.session.flush()
        uploader = await self.user_repo.get(item.uploader_id)
        resp = ModerationItemResponse.model_validate(item)
        resp.uploader_name = uploader.full_name if uploader else "Unknown"
        return resp
