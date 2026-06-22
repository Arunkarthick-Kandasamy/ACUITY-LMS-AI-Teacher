from __future__ import annotations

import logging
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.common.types import UserRole
from app.content_ingestion.ai.curriculum_generator import CurriculumGenerator
from app.content_ingestion.ai.extractor import ContentExtractor
from app.content_ingestion.models import ContentUpload, CurriculumDraft, DraftStatus, UploadStatus
from app.content_ingestion.parsers import get_file_type, parse_file
from app.content_ingestion.repository import ContentUploadRepository, CurriculumDraftRepository
from app.curriculum.service import CourseService
from app.knowledge_graph.service import KnowledgeGraphService
from app.users.models import User

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent / "uploads"


class ContentIngestionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.upload_repo = ContentUploadRepository(session)
        self.draft_repo = CurriculumDraftRepository(session)
        self.course_service = CourseService(session)
        self.kg_service = KnowledgeGraphService(session)
        self.extractor = ContentExtractor()
        self.curriculum_gen = CurriculumGenerator(self.course_service, self.kg_service)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self, current_user: User, filename: str, content: bytes
    ) -> ContentUpload:
        file_type = get_file_type(filename)
        if file_type is None:
            supported = ", ".join(sorted(p.upper() for p in ("txt", "pdf", "docx")))
            raise ValidationException(
                message=f"Unsupported file type. Supported: {supported}",
                code="UNSUPPORTED_FILE_TYPE",
            )

        file_size = len(content)
        if file_size == 0:
            raise ValidationException(message="Uploaded file is empty", code="EMPTY_FILE")
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            raise ValidationException(
                message=f"File too large. Maximum size is {max_size // (1024*1024)}MB",
                code="FILE_TOO_LARGE",
            )

        stored_path = await self._save_file(content, filename)

        upload = await self.upload_repo.create(
            user_id=current_user.id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_path=str(stored_path),
            status=UploadStatus.PENDING,
        )

        try:
            upload.status = UploadStatus.EXTRACTING
            await self.session.flush()

            extracted_text = parse_file(str(stored_path), file_type)
            upload.extracted_text = extracted_text
            upload.status = UploadStatus.COMPLETED
            await self.session.flush()
            await self.session.refresh(upload)
        except Exception as e:
            upload.status = UploadStatus.FAILED
            upload.error_message = str(e)
            await self.session.flush()
            await self.session.refresh(upload)
            logger.error("File extraction failed for %s: %s", filename, e)

        return upload

    async def get_job(self, current_user: User, upload_id: str) -> ContentUpload:
        upload = await self.upload_repo.get(upload_id)
        if upload is None:
            raise NotFoundException(message="Upload job not found")
        self._verify_access(current_user, upload.user_id)
        return upload

    async def generate_draft(self, current_user: User, upload_id: str) -> CurriculumDraft:
        upload = await self.upload_repo.get(upload_id)
        if upload is None:
            raise NotFoundException(message="Upload not found")
        self._verify_access(current_user, upload.user_id)

        if upload.status != UploadStatus.COMPLETED:
            raise ConflictException(
                message="Upload has not completed extraction yet",
                code="EXTRACTION_NOT_COMPLETE",
            )
        if not upload.extracted_text:
            raise ConflictException(
                message="No extracted text available for this upload",
                code="NO_EXTRACTED_TEXT",
            )

        existing_draft = await self.draft_repo.find_by_upload(upload_id)
        if existing_draft is not None:
            return existing_draft

        extracted_data = await self.extractor.extract(upload.extracted_text)

        draft = await self.draft_repo.create(
            upload_id=upload_id,
            created_by=current_user.id,
            title=extracted_data.get("title", upload.filename)[:300],
            status=DraftStatus.DRAFT,
            generated_data=extracted_data,
        )
        return draft

    async def get_draft(self, current_user: User, draft_id: str) -> CurriculumDraft:
        draft = await self.draft_repo.get(draft_id)
        if draft is None:
            raise NotFoundException(message="Draft not found")
        self._verify_access(current_user, draft.created_by)
        return draft

    async def approve_draft(self, current_user: User, draft_id: str) -> CurriculumDraft:
        draft = await self.draft_repo.get(draft_id)
        if draft is None:
            raise NotFoundException(message="Draft not found")
        self._verify_access(current_user, draft.created_by)

        if draft.status == DraftStatus.PUBLISHED:
            raise ConflictException(
                message="Cannot approve a draft that has already been published",
                code="ALREADY_PUBLISHED",
            )

        draft.status = DraftStatus.APPROVED
        await self.session.flush()
        await self.session.refresh(draft)
        return draft

    async def publish_draft(self, current_user: User, draft_id: str) -> CurriculumDraft:
        draft = await self.draft_repo.get(draft_id)
        if draft is None:
            raise NotFoundException(message="Draft not found")
        self._verify_access(current_user, draft.created_by)

        if draft.status == DraftStatus.PUBLISHED:
            raise ConflictException(
                message="Draft has already been published",
                code="ALREADY_PUBLISHED",
            )
        if draft.status != DraftStatus.APPROVED:
            raise ConflictException(
                message="Draft must be approved before publishing. Call approve first.",
                code="NOT_APPROVED",
            )
        if not draft.generated_data:
            raise ConflictException(
                message="Draft has no generated data to publish",
                code="NO_GENERATED_DATA",
            )

        try:
            course_id = await self.curriculum_gen.publish(current_user.id, draft.generated_data)
            draft.course_id = course_id
            draft.status = DraftStatus.PUBLISHED
            await self.session.flush()
            await self.session.refresh(draft)
        except Exception as e:
            logger.error("Failed to publish draft %s: %s", draft_id, e)
            raise ConflictException(
                message=f"Failed to publish draft: {e}",
                code="PUBLISH_FAILED",
            ) from e

        return draft

    async def _save_file(self, content: bytes, filename: str) -> Path:
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = UPLOAD_DIR / unique_name
        file_path.write_bytes(content)
        return file_path

    @staticmethod
    def _verify_access(current_user: User, owner_id: str) -> None:
        if current_user.role != UserRole.ADMIN and current_user.id != owner_id:
            raise ForbiddenException(
                message="You do not have access to this resource",
                code="ACCESS_DENIED",
            )
