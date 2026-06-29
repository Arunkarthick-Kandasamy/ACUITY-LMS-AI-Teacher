from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.content_ingestion.schemas import (
    ApproveResponse,
    DraftResponse,
    JobStatusResponse,
    PublishResponse,
    UploadResponse,
)
from app.content_ingestion.service import ContentIngestionService
from app.infrastructure.database import get_session
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/content", tags=["Content Ingestion"])

teacher_admin = require_roles(UserRole.ADMIN, UserRole.COURSE_ADMIN)


async def _draft_to_response(draft) -> dict:
    from app.content_ingestion.schemas import CurriculumData

    curriculum = None
    if draft.generated_data:
        curriculum = CurriculumData(**draft.generated_data)
    return DraftResponse(
        draft_id=draft.id,
        upload_id=draft.upload_id,
        title=draft.title,
        status=draft.status,
        curriculum=curriculum,
        course_id=draft.course_id,
        created_by=draft.created_by,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    ).model_dump(mode="json")


@router.post("/upload", status_code=201)
async def upload_content(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(teacher_admin),
) -> dict:
    service = ContentIngestionService(session)
    content = await file.read()
    upload = await service.upload_file(current_user, file.filename or "untitled", content)
    return success_response(
        UploadResponse(
            upload_id=upload.id,
            filename=upload.filename,
            file_type=upload.file_type,
            file_size=upload.file_size,
            status=upload.status,
            created_at=upload.created_at,
        ).model_dump(mode="json")
    )


@router.get("/jobs/{upload_id}")
async def get_job_status(
    upload_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ContentIngestionService(session)
    upload = await service.get_job(current_user, upload_id)
    draft = None
    from app.content_ingestion.repository import CurriculumDraftRepository
    draft_repo = CurriculumDraftRepository(session)
    draft = await draft_repo.find_by_upload(upload_id)
    return success_response(
        JobStatusResponse(
            upload_id=upload.id,
            filename=upload.filename,
            file_type=upload.file_type,
            status=upload.status,
            error_message=upload.error_message,
            draft_id=draft.id if draft else None,
            created_at=upload.created_at,
            updated_at=upload.updated_at,
        ).model_dump(mode="json")
    )


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ContentIngestionService(session)
    draft = await service.get_draft(current_user, draft_id)
    return success_response(await _draft_to_response(draft))


@router.post("/drafts/{draft_id}/generate")
async def generate_draft(
    draft_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(teacher_admin),
) -> dict:
    service = ContentIngestionService(session)
    draft = await service.generate_draft(current_user, draft_id)
    return success_response(await _draft_to_response(draft))


@router.post("/drafts/{draft_id}/approve")
async def approve_draft(
    draft_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(teacher_admin),
) -> dict:
    service = ContentIngestionService(session)
    draft = await service.approve_draft(current_user, draft_id)
    return success_response(
        ApproveResponse(
            draft_id=draft.id,
            status=draft.status,
            updated_at=draft.updated_at,
        ).model_dump(mode="json")
    )


@router.post("/drafts/{draft_id}/publish")
async def publish_draft(
    draft_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(teacher_admin),
) -> dict:
    service = ContentIngestionService(session)
    draft = await service.publish_draft(current_user, draft_id)
    return success_response(
        PublishResponse(
            draft_id=draft.id,
            status=draft.status,
            course_id=draft.course_id or "",
            course_title=draft.title,
            updated_at=draft.updated_at,
        ).model_dump(mode="json")
    )
