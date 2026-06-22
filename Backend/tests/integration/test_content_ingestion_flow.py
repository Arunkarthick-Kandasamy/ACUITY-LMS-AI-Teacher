from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.common.types import UserRole
from app.content_ingestion.models import ContentUpload, CurriculumDraft, DraftStatus, UploadStatus
from app.content_ingestion.service import ContentIngestionService
from app.users.models import User


class TestContentIngestionFlow:
    @pytest.mark.asyncio
    async def test_full_upload_to_publish_flow(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = Mock(spec=User)
        admin.id = "admin-1"
        admin.role = UserRole.ADMIN
        admin.is_active = True

        test_content = b"Course: Python Programming\nModule 1: Getting Started\nLesson 1: Hello World\nConcept: Print statements"

        upload = Mock(spec=ContentUpload)
        upload.id = "upload-1"
        upload.user_id = "admin-1"
        upload.filename = "course.txt"
        upload.file_type = "txt"
        upload.file_size = len(test_content)
        upload.status = UploadStatus.PENDING
        upload.extracted_text = None
        upload.error_message = None

        service.upload_repo.create = AsyncMock(return_value=upload)

        with (
            patch.object(service, "_save_file", AsyncMock(return_value=Path("/tmp/course.txt"))),
            patch("app.content_ingestion.service.parse_file", return_value=test_content.decode("utf-8")),
        ):
            result = await service.upload_file(admin, "course.txt", test_content)

        assert result.status == UploadStatus.COMPLETED
        assert result.extracted_text is not None

        service.upload_repo.get = AsyncMock(return_value=upload)
        service.draft_repo.find_by_upload = AsyncMock(return_value=None)

        extracted_data = {
            "title": "Python Programming",
            "description": "Learn Python",
            "total_duration_hours": 30,
            "default_deadline_days": 60,
            "modules": [
                {
                    "title": "Getting Started",
                    "description": "First steps",
                    "order_index": 1,
                    "estimated_duration_hours": 5,
                    "lessons": [
                        {
                            "title": "Hello World",
                            "order_index": 1,
                            "estimated_duration_minutes": 20,
                            "is_required": True,
                            "concepts": [
                                {
                                    "title": "Print statements",
                                    "description": "Using print",
                                    "order_index": 1,
                                    "estimated_duration_minutes": 10,
                                    "contents": [
                                        {"content_type": "explanation", "content": "Print outputs text", "order_index": 0}
                                    ],
                                    "exercises": [],
                                    "examples": [],
                                }
                            ],
                            "objectives": [],
                        }
                    ],
                }
            ],
            "knowledge_graph": [],
        }

        with patch.object(service.extractor, "extract", AsyncMock(return_value=extracted_data)):
            draft = Mock(spec=CurriculumDraft)
            draft.id = "draft-1"
            draft.upload_id = "upload-1"
            draft.created_by = "admin-1"
            draft.title = "Python Programming"
            draft.status = DraftStatus.DRAFT
            draft.generated_data = extracted_data
            draft.course_id = None

            service.draft_repo.create = AsyncMock(return_value=draft)

            result_draft = await service.generate_draft(admin, "upload-1")

        assert result_draft.id == "draft-1"
        assert result_draft.status == DraftStatus.DRAFT

        service.draft_repo.get = AsyncMock(return_value=draft)

        draft.status = DraftStatus.APPROVED
        result_approve = await service.approve_draft(admin, "draft-1")
        assert result_approve.status == DraftStatus.APPROVED

        draft.status = DraftStatus.APPROVED
        draft.course_id = None
        service.draft_repo.get = AsyncMock(return_value=draft)

        with patch.object(service.curriculum_gen, "publish", AsyncMock(return_value="course-1")):
            published = await service.publish_draft(admin, "draft-1")

        assert published.status == DraftStatus.PUBLISHED
        assert published.course_id == "course-1"
