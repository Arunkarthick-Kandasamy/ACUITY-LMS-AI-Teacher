from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.content_ingestion.models import ContentUpload, CurriculumDraft, UploadStatus


class ContentUploadRepository(Repository[ContentUpload]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(ContentUpload, session)

    async def find_by_user(self, user_id: str, limit: int = 20, offset: int = 0) -> list[ContentUpload]:
        stmt = (
            select(ContentUpload)
            .where(ContentUpload.user_id == user_id)
            .order_by(ContentUpload.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_pending(self) -> list[ContentUpload]:
        stmt = select(ContentUpload).where(ContentUpload.status == UploadStatus.PENDING)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class CurriculumDraftRepository(Repository[CurriculumDraft]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(CurriculumDraft, session)

    async def find_by_user(self, user_id: str, limit: int = 20, offset: int = 0) -> list[CurriculumDraft]:
        stmt = (
            select(CurriculumDraft)
            .where(CurriculumDraft.created_by == user_id)
            .order_by(CurriculumDraft.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_upload(self, upload_id: str) -> CurriculumDraft | None:
        stmt = select(CurriculumDraft).where(CurriculumDraft.upload_id == upload_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
