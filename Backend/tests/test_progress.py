from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.common.exceptions import NotFoundException
from app.common.types import LessonProgressStatus
from app.progress.service import ProgressService
from app.teaching.models import Attempt, LessonProgress


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_student_profile() -> MagicMock:
    profile = MagicMock()
    profile.id = "sp-1"
    profile.user_id = "user-1"
    return profile


@pytest.fixture
def mock_lesson() -> MagicMock:
    lesson = MagicMock()
    lesson.id = "lsn-1"
    lesson.module_id = "mod-1"
    lesson.title = "Test Lesson"
    return lesson


@pytest.fixture
def mock_course() -> MagicMock:
    course = MagicMock()
    course.id = "course-1"
    course.code = "CS101"
    course.title = "Intro"
    course.modules = []
    return course


def _make_lesson_progress(**overrides) -> LessonProgress:
    defaults = dict(
        id="lp-1",
        student_id="sp-1",
        lesson_id="lsn-1",
        status=LessonProgressStatus.IN_PROGRESS,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        time_spent_seconds=120,
        completion_percentage=50.0,
    )
    defaults.update(overrides)
    return LessonProgress(**defaults)


# ---------------------------------------------------------------------------
# ProgressService
# ---------------------------------------------------------------------------

class TestProgressService:
    @pytest.mark.asyncio
    async def test_get_curriculum_tree(self, mock_session, mock_course) -> None:
        service = ProgressService(mock_session)
        service.course_repo.get = AsyncMock(return_value=mock_course)

        course = await service.get_curriculum_tree("course-1")
        assert course.id == "course-1"

    @pytest.mark.asyncio
    async def test_get_curriculum_tree_not_found(self, mock_session) -> None:
        service = ProgressService(mock_session)
        service.course_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_curriculum_tree("nonexistent")

    @pytest.mark.asyncio
    async def test_get_lesson_progress(self, mock_session, mock_student_profile) -> None:
        service = ProgressService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.progress_repo.find_by_student_and_lesson = AsyncMock(
            return_value=_make_lesson_progress()
        )

        progress = await service.get_lesson_progress("lsn-1", "user-1")
        assert progress is not None
        assert progress.id == "lp-1"

    @pytest.mark.asyncio
    async def test_get_lesson_progress_none(self, mock_session, mock_student_profile) -> None:
        service = ProgressService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.progress_repo.find_by_student_and_lesson = AsyncMock(return_value=None)

        progress = await service.get_lesson_progress("lsn-1", "user-1")
        assert progress is None

    @pytest.mark.asyncio
    async def test_update_lesson_progress_create(self, mock_session, mock_student_profile, mock_lesson) -> None:
        service = ProgressService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.lesson_repo.get = AsyncMock(return_value=mock_lesson)
        service.progress_repo.find_by_student_and_lesson = AsyncMock(return_value=None)
        service.progress_repo.create = AsyncMock(return_value=_make_lesson_progress(
            status=LessonProgressStatus.IN_PROGRESS
        ))

        progress = await service.update_lesson_progress(
            "lsn-1", "user-1", status=LessonProgressStatus.IN_PROGRESS
        )
        assert progress.status == LessonProgressStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_update_lesson_progress_complete(self, mock_session, mock_student_profile, mock_lesson) -> None:
        service = ProgressService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.lesson_repo.get = AsyncMock(return_value=mock_lesson)
        service.progress_repo.find_by_student_and_lesson = AsyncMock(
            return_value=_make_lesson_progress()
        )
        service.progress_repo.update = AsyncMock(return_value=_make_lesson_progress(
            status=LessonProgressStatus.COMPLETED,
            completion_percentage=100.0,
        ))

        progress = await service.update_lesson_progress(
            "lsn-1", "user-1", status=LessonProgressStatus.COMPLETED
        )
        assert progress.status == LessonProgressStatus.COMPLETED
        assert progress.completion_percentage == 100.0

    @pytest.mark.asyncio
    async def test_record_attempt(self, mock_session, mock_student_profile) -> None:
        service = ProgressService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)

        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=0)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service.attempt_repo.create = AsyncMock(return_value=Attempt(
            id="at-1",
            student_id="sp-1",
            exercise_id="exr-1",
            teaching_session_id=None,
            response="Answer",
            is_correct=True,
            score=1.0,
            time_taken_seconds=30,
            attempt_number=1,
            attempted_at=datetime.now(timezone.utc),
            ai_feedback=None,
            attempt_metadata={},
        ))

        with patch("app.mastery.service.MasteryService.recalculate_mastery", new=AsyncMock()):
            attempt = await service.record_attempt(
                user_id="user-1",
                exercise_id="exr-1",
                response="Answer",
                is_correct=True,
                score=1.0,
                time_taken_seconds=30,
            )
            assert attempt.is_correct is True
            assert attempt.attempt_number == 1

    @pytest.mark.asyncio
    async def test_get_attempt_history(self, mock_session, mock_student_profile) -> None:
        service = ProgressService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.attempt_repo.find_by_student = AsyncMock(return_value=([], 0))

        attempts, total = await service.get_attempt_history("user-1")
        assert len(attempts) == 0
        assert total == 0
