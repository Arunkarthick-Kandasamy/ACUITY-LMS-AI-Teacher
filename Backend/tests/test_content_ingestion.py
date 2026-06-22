from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.common.types import NodeType, UserRole
from app.content_ingestion.ai.curriculum_generator import CurriculumGenerator
from app.content_ingestion.ai.extractor import ContentExtractor
from app.content_ingestion.models import ContentUpload, CurriculumDraft, DraftStatus, UploadStatus
from app.content_ingestion.parsers import get_file_type, parse_file
from app.content_ingestion.repository import ContentUploadRepository, CurriculumDraftRepository
from app.content_ingestion.schemas import (
    ConceptContentItem,
    ConceptItem,
    CurriculumData,
    DraftResponse,
    ExerciseItem,
    JobStatusResponse,
    KnowledgeGraphEdge,
    LessonItem,
    ModuleItem,
    ObjectiveItem,
    UploadResponse,
)
from app.content_ingestion.service import ContentIngestionService
from app.curriculum.models import Concept, Course, Lesson, Module
from app.curriculum.service import CourseService
from app.knowledge_graph.models import KnowledgeNode
from app.knowledge_graph.service import KnowledgeGraphService
from app.users.models import User

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_user(
    user_id: str = "user-1",
    role: UserRole = UserRole.ADMIN,
    full_name: str = "Test Admin",
) -> User:
    user = Mock(spec=User)
    user.id = user_id
    user.role = role
    user.full_name = full_name
    user.email = "admin@test.com"
    user.is_active = True
    return user


def _make_upload(**overrides) -> ContentUpload:
    upload = Mock(spec=ContentUpload)
    defaults = dict(
        id="upload-1",
        user_id="user-1",
        filename="test.txt",
        file_type="txt",
        file_size=1024,
        file_path="/tmp/test.txt",
        status=UploadStatus.COMPLETED,
        extracted_text="Course: Math 101\nModule 1: Algebra\nLesson 1: Variables\nConcept: What is a variable?",
        error_message=None,
        created_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(upload, k, v)
    return upload


def _make_draft(**overrides) -> CurriculumDraft:
    draft = Mock(spec=CurriculumDraft)
    defaults = dict(
        id="draft-1",
        upload_id="upload-1",
        created_by="user-1",
        title="Math 101",
        status=DraftStatus.DRAFT,
        generated_data={
            "title": "Math 101",
            "description": "Basic math course",
            "total_duration_hours": 40,
            "default_deadline_days": 90,
            "modules": [
                {
                    "title": "Algebra",
                    "description": "Algebra module",
                    "order_index": 1,
                    "estimated_duration_hours": 10,
                    "lessons": [
                        {
                            "title": "Variables",
                            "order_index": 1,
                            "estimated_duration_minutes": 30,
                            "is_required": True,
                            "concepts": [
                                {
                                    "title": "What is a Variable?",
                                    "description": "Define variables",
                                    "order_index": 1,
                                    "estimated_duration_minutes": 15,
                                    "contents": [],
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
        },
        course_id=None,
        created_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(draft, k, v)
    return draft


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TestSchemas:
    def test_upload_response(self) -> None:
        data = UploadResponse(
            upload_id="u-1",
            filename="test.txt",
            file_type="txt",
            file_size=1024,
            status="completed",
            created_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
        )
        assert data.upload_id == "u-1"
        assert data.filename == "test.txt"

    def test_job_status_response(self) -> None:
        data = JobStatusResponse(
            upload_id="u-1",
            filename="test.txt",
            file_type="txt",
            status="completed",
            draft_id="d-1",
            created_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
            updated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
        )
        assert data.draft_id == "d-1"
        assert data.status == "completed"

    def test_curriculum_data_nested(self) -> None:
        data = CurriculumData(
            title="Math 101",
            description="Basic math",
            total_duration_hours=40,
            default_deadline_days=90,
            modules=[
                ModuleItem(
                    title="Algebra",
                    order_index=1,
                    estimated_duration_hours=10,
                    lessons=[
                        LessonItem(
                            title="Variables",
                            order_index=1,
                            estimated_duration_minutes=30,
                            concepts=[
                                ConceptItem(
                                    title="What is a Variable?",
                                    order_index=1,
                                    contents=[
                                        ConceptContentItem(
                                            content_type="explanation",
                                            content="A variable stores data.",
                                            order_index=0,
                                        )
                                    ],
                                    exercises=[
                                        ExerciseItem(
                                            question_type="mcq",
                                            prompt="What is x?",
                                            options={"A": "1", "B": "2"},
                                            correct_answer="A",
                                            order_index=1,
                                        )
                                    ],
                                )
                            ],
                            objectives=[
                                ObjectiveItem(
                                    code="MOD1.LSN1.01",
                                    description="Define variables",
                                    order_index=1,
                                )
                            ],
                        )
                    ],
                )
            ],
            knowledge_graph=[
                KnowledgeGraphEdge(
                    source_concept_title="Numbers",
                    target_concept_title="Variables",
                    relationship="requires",
                    weight=0.9,
                )
            ],
        )
        assert len(data.modules) == 1
        assert len(data.modules[0].lessons) == 1
        assert len(data.modules[0].lessons[0].concepts) == 1
        assert len(data.modules[0].lessons[0].concepts[0].contents) == 1
        assert len(data.modules[0].lessons[0].concepts[0].exercises) == 1
        assert len(data.modules[0].lessons[0].objectives) == 1
        assert len(data.knowledge_graph) == 1


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

class TestParsers:
    def test_get_file_type(self) -> None:
        assert get_file_type("doc.txt") == "txt"
        assert get_file_type("doc.pdf") == "pdf"
        assert get_file_type("doc.docx") == "docx"
        assert get_file_type("doc.doc") is None
        assert get_file_type("file") is None

    def test_parse_txt(self, tmp_path: Path) -> None:
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello World", encoding="utf-8")
        result = parse_file(str(file_path), "txt")
        assert result == "Hello World"

    def test_parse_txt_unicode(self, tmp_path: Path) -> None:
        file_path = tmp_path / "test.txt"
        file_path.write_text("Café résumé ñoño", encoding="utf-8")
        result = parse_file(str(file_path), "txt")
        assert "Café" in result

    def test_parse_unsupported_type(self) -> None:
        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_file("test.xyz", "xyz")


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

class TestContentExtractor:
    @pytest.mark.asyncio
    async def test_extract_with_gemini(self) -> None:
        raw = "Course: Python Programming\nModule 1: Basics"
        expected = {
            "title": "Python Programming",
            "description": "Learn Python from scratch",
            "total_duration_hours": 30,
            "default_deadline_days": 60,
            "modules": [
                {
                    "title": "Basics",
                    "description": "Python basics",
                    "order_index": 1,
                    "estimated_duration_hours": 5,
                    "lessons": [],
                }
            ],
            "knowledge_graph": [],
        }

        extractor = ContentExtractor()
        with patch.object(extractor.gemini, "generate_json", AsyncMock(return_value=expected)):
            result = await extractor.extract(raw)

        assert result["title"] == "Python Programming"
        assert len(result["modules"]) == 1

    @pytest.mark.asyncio
    async def test_extract_fallback_on_failure(self) -> None:
        raw = "Some educational content"
        extractor = ContentExtractor()
        with patch.object(extractor.gemini, "generate_json", AsyncMock(side_effect=Exception("API error"))):
            result = await extractor.extract(raw)

        assert "title" in result
        assert "modules" in result
        assert len(result["modules"]) == 1

    @pytest.mark.asyncio
    async def test_extract_validates_output(self) -> None:
        raw = "content"
        bad_data = {
            "title": 123,
            "description": None,
            "total_duration_hours": "forty",
            "default_deadline_days": None,
            "modules": "not a list",
            "knowledge_graph": None,
        }
        extractor = ContentExtractor()
        with patch.object(extractor.gemini, "generate_json", AsyncMock(return_value=bad_data)):
            result = await extractor.extract(raw)

        assert isinstance(result["title"], str)
        assert isinstance(result["total_duration_hours"], int)
        assert isinstance(result["modules"], list)
        assert isinstance(result["knowledge_graph"], list)


# ---------------------------------------------------------------------------
# Curriculum Generator
# ---------------------------------------------------------------------------

class TestCurriculumGenerator:
    @pytest.mark.asyncio
    async def test_generate_code(self) -> None:
        code = CurriculumGenerator._generate_code("Python Programming")
        assert code.startswith("PYTHON-PROGRAMMING-")
        assert len(code) > 20

    @pytest.mark.asyncio
    async def test_generate_code_empty_title(self) -> None:
        code = CurriculumGenerator._generate_code("")
        assert code.startswith("COURSE-")

    @pytest.mark.asyncio
    async def test_publish_creates_course(self) -> None:
        session = AsyncMock()
        course_service = CourseService(session)
        kg_service = KnowledgeGraphService(session)
        generator = CurriculumGenerator(course_service, kg_service)

        mock_course = Mock(spec=Course)
        mock_course.id = "course-1"
        course_service.create_course = AsyncMock(return_value=mock_course)

        mock_module = Mock(spec=Module)
        mock_module.id = "mod-1"
        course_service.create_module = AsyncMock(return_value=mock_module)

        mock_lesson = Mock(spec=Lesson)
        mock_lesson.id = "lsn-1"
        mock_lesson.order_index = 1
        course_service.create_lesson = AsyncMock(return_value=mock_lesson)

        mock_concept = Mock(spec=Concept)
        mock_concept.id = "con-1"
        mock_concept.title = "Variables"
        course_service.create_concept = AsyncMock(return_value=mock_concept)

        mock_node = Mock(spec=KnowledgeNode)
        mock_node.id = "node-1"
        kg_service.node_repo.create = AsyncMock(return_value=mock_node)

        course_service.lesson_repo.get = AsyncMock(return_value=mock_lesson)
        course_service.objective_repo.get_max_order = AsyncMock(return_value=0)
        course_service.concept_repo.get = AsyncMock(return_value=mock_concept)
        course_service.content_repo.get_max_order = AsyncMock(return_value=0)
        course_service.exercise_repo.get_max_order = AsyncMock(return_value=0)
        course_service.example_repo.get_max_order = AsyncMock(return_value=0)

        data = {
            "title": "Python 101",
            "description": "Intro",
            "total_duration_hours": 20,
            "default_deadline_days": 45,
            "modules": [
                {
                    "title": "Basics",
                    "description": "Basic module",
                    "order_index": 1,
                    "estimated_duration_hours": 5,
                    "lessons": [
                        {
                            "title": "Variables",
                            "order_index": 1,
                            "estimated_duration_minutes": 30,
                            "is_required": True,
                            "concepts": [
                                {
                                    "title": "Variables",
                                    "description": "Variables explained",
                                    "order_index": 1,
                                    "estimated_duration_minutes": 15,
                                    "contents": [
                                        {"content_type": "explanation", "content": "A variable...", "order_index": 0}
                                    ],
                                    "exercises": [
                                        {
                                            "question_type": "mcq",
                                            "prompt": "What is x?",
                                            "options": {"A": "1"},
                                            "correct_answer": "A",
                                            "difficulty": 0.5,
                                            "order_index": 1,
                                        }
                                    ],
                                    "examples": [
                                        {"content": "x = 5", "explanation": "Simple", "order_index": 1, "tags": ["basic"]}
                                    ],
                                }
                            ],
                            "objectives": [
                                {"code": "MOD1.LSN1.01", "description": "Define var", "order_index": 1}
                            ],
                        }
                    ],
                }
            ],
            "knowledge_graph": [],
        }

        result = await generator.publish("user-1", data)
        assert result == "course-1"

    @pytest.mark.asyncio
    async def test_publish_with_knowledge_graph(self) -> None:
        session = AsyncMock()
        course_service = CourseService(session)
        kg_service = KnowledgeGraphService(session)
        generator = CurriculumGenerator(course_service, kg_service)

        mock_course = Mock(spec=Course)
        mock_course.id = "course-1"
        course_service.create_course = AsyncMock(return_value=mock_course)

        mock_module = Mock(spec=Module)
        mock_module.id = "mod-1"
        course_service.create_module = AsyncMock(return_value=mock_module)

        mock_lesson = Mock(spec=Lesson)
        mock_lesson.id = "lsn-1"
        mock_lesson.order_index = 1
        course_service.create_lesson = AsyncMock(return_value=mock_lesson)

        mock_concept1 = Mock(spec=Concept)
        mock_concept1.id = "con-1"
        mock_concept1.title = "Numbers"
        mock_concept2 = Mock(spec=Concept)
        mock_concept2.id = "con-2"
        mock_concept2.title = "Variables"
        course_service.create_concept = AsyncMock(side_effect=[mock_concept1, mock_concept2])

        mock_node1 = Mock(spec=KnowledgeNode)
        mock_node1.id = "node-1"
        mock_node2 = Mock(spec=KnowledgeNode)
        mock_node2.id = "node-2"
        kg_service.node_repo.create = AsyncMock(side_effect=[mock_node1, mock_node2])

        data = {
            "title": "Math",
            "description": "",
            "total_duration_hours": 20,
            "default_deadline_days": 45,
            "modules": [
                {
                    "title": "Basics",
                    "description": "",
                    "order_index": 1,
                    "estimated_duration_hours": 5,
                    "lessons": [
                        {
                            "title": "Fundamentals",
                            "order_index": 1,
                            "estimated_duration_minutes": 30,
                            "is_required": True,
                            "concepts": [
                                {
                                    "title": "Numbers",
                                    "description": "",
                                    "order_index": 1,
                                    "estimated_duration_minutes": 15,
                                    "contents": [],
                                    "exercises": [],
                                    "examples": [],
                                },
                                {
                                    "title": "Variables",
                                    "description": "",
                                    "order_index": 2,
                                    "estimated_duration_minutes": 15,
                                    "contents": [],
                                    "exercises": [],
                                    "examples": [],
                                },
                            ],
                            "objectives": [],
                        }
                    ],
                }
            ],
            "knowledge_graph": [
                {
                    "source_concept_title": "Numbers",
                    "target_concept_title": "Variables",
                    "relationship": "requires",
                    "weight": 0.9,
                }
            ],
        }

        result = await generator.publish("user-1", data)
        assert result == "course-1"


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class TestContentIngestionService:
    @pytest.mark.asyncio
    async def test_upload_file_success(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        service.upload_repo.create = AsyncMock(
            return_value=_make_upload(status=UploadStatus.PENDING)
        )

        with (
            patch.object(service, "_save_file", AsyncMock(return_value=Path("/tmp/test.txt"))),
            patch("app.content_ingestion.service.parse_file", return_value="Extracted text") as mock_parse,
        ):
            result = await service.upload_file(admin, "test.txt", b"content")

        assert result.status == UploadStatus.COMPLETED
        assert result.extracted_text == "Extracted text"
        mock_parse.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_unsupported_type(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        with pytest.raises(ValidationException, match="Unsupported file type"):
            await service.upload_file(admin, "test.exe", b"content")

    @pytest.mark.asyncio
    async def test_upload_file_empty(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        with pytest.raises(ValidationException, match="empty"):
            await service.upload_file(admin, "test.txt", b"")

    @pytest.mark.asyncio
    async def test_upload_file_extraction_failure(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        service.upload_repo.create = AsyncMock(
            return_value=_make_upload(status=UploadStatus.PENDING)
        )

        with (
            patch.object(service, "_save_file", AsyncMock(return_value=Path("/tmp/test.txt"))),
            patch("app.content_ingestion.service.parse_file", side_effect=RuntimeError("Parse error")),
        ):
            result = await service.upload_file(admin, "test.txt", b"content")

        assert result.status == UploadStatus.FAILED
        assert "Parse error" in (result.error_message or "")

    @pytest.mark.asyncio
    async def test_get_job_found(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        service.upload_repo.get = AsyncMock(return_value=_make_upload())

        result = await service.get_job(admin, "upload-1")
        assert result.id == "upload-1"

    @pytest.mark.asyncio
    async def test_get_job_not_found(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        service.upload_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_job(admin, "nonexistent")

    @pytest.mark.asyncio
    async def test_get_job_forbidden(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        other_user = _make_user(user_id="user-2", role=UserRole.STUDENT)

        upload = _make_upload(user_id="user-1")
        service.upload_repo.get = AsyncMock(return_value=upload)

        with pytest.raises(ForbiddenException):
            await service.get_job(other_user, "upload-1")

    @pytest.mark.asyncio
    async def test_generate_draft_success(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        upload = _make_upload(status=UploadStatus.COMPLETED, extracted_text="some content")
        service.upload_repo.get = AsyncMock(return_value=upload)
        service.draft_repo.find_by_upload = AsyncMock(return_value=None)

        expected_data = {"title": "Generated Course", "description": "", "total_duration_hours": 40, "default_deadline_days": 90, "modules": [], "knowledge_graph": []}

        with patch.object(service.extractor, "extract", AsyncMock(return_value=expected_data)):
            service.draft_repo.create = AsyncMock(return_value=_make_draft())

            result = await service.generate_draft(admin, "upload-1")

        assert result.id == "draft-1"

    @pytest.mark.asyncio
    async def test_generate_draft_already_exists(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        upload = _make_upload(status=UploadStatus.COMPLETED)
        service.upload_repo.get = AsyncMock(return_value=upload)
        service.draft_repo.find_by_upload = AsyncMock(return_value=_make_draft())

        result = await service.generate_draft(admin, "upload-1")
        assert result.id == "draft-1"

    @pytest.mark.asyncio
    async def test_generate_draft_extraction_not_complete(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        upload = _make_upload(status=UploadStatus.FAILED)
        service.upload_repo.get = AsyncMock(return_value=upload)

        with pytest.raises(ConflictException, match="not completed"):
            await service.generate_draft(admin, "upload-1")

    @pytest.mark.asyncio
    async def test_approve_draft(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        draft = _make_draft(status=DraftStatus.DRAFT)
        service.draft_repo.get = AsyncMock(return_value=draft)

        result = await service.approve_draft(admin, "draft-1")
        assert result.status == DraftStatus.APPROVED

    @pytest.mark.asyncio
    async def test_approve_already_published(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        draft = _make_draft(status=DraftStatus.PUBLISHED)
        service.draft_repo.get = AsyncMock(return_value=draft)

        with pytest.raises(ConflictException, match="already been published"):
            await service.approve_draft(admin, "draft-1")

    @pytest.mark.asyncio
    async def test_publish_draft_success(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        draft = _make_draft(status=DraftStatus.APPROVED)
        service.draft_repo.get = AsyncMock(return_value=draft)

        mock_course_id = "course-1"
        with patch.object(service.curriculum_gen, "publish", AsyncMock(return_value=mock_course_id)):
            result = await service.publish_draft(admin, "draft-1")

        assert result.status == DraftStatus.PUBLISHED
        assert result.course_id == "course-1"

    @pytest.mark.asyncio
    async def test_publish_draft_not_approved(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        draft = _make_draft(status=DraftStatus.DRAFT)
        service.draft_repo.get = AsyncMock(return_value=draft)

        with pytest.raises(ConflictException, match="must be approved"):
            await service.publish_draft(admin, "draft-1")

    @pytest.mark.asyncio
    async def test_publish_draft_not_found(self) -> None:
        session = AsyncMock()
        service = ContentIngestionService(session)
        admin = _make_user()

        service.draft_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.publish_draft(admin, "nonexistent")

    @pytest.mark.asyncio
    async def test_verify_access_admin(self) -> None:
        admin = _make_user()
        ContentIngestionService._verify_access(admin, "other-user-id")
        # No exception means success

    @pytest.mark.asyncio
    async def test_verify_access_owner(self) -> None:
        owner = _make_user(user_id="owner-1", role=UserRole.STUDENT)
        ContentIngestionService._verify_access(owner, "owner-1")
        # No exception means success

    @pytest.mark.asyncio
    async def test_verify_access_forbidden(self) -> None:
        other = _make_user(user_id="other-1", role=UserRole.STUDENT)
        with pytest.raises(ForbiddenException):
            ContentIngestionService._verify_access(other, "owner-1")
