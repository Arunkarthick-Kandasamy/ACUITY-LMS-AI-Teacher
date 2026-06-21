from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import ConflictException, NotFoundException, ValidationException
from app.common.types import SessionState
from app.teaching.models import TeachingSession
from app.teaching_sessions.service import SessionService


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
def mock_course() -> MagicMock:
    course = MagicMock()
    course.id = "course-1"
    course.code = "CS101"
    course.title = "Intro to CS"
    return course


@pytest.fixture
def mock_lesson() -> MagicMock:
    lesson = MagicMock()
    lesson.id = "lsn-1"
    lesson.title = "Test Lesson"
    return lesson


@pytest.fixture
def mock_concept() -> MagicMock:
    concept = MagicMock()
    concept.id = "con-1"
    concept.title = "Test Concept"
    return concept


def _make_session(**overrides) -> TeachingSession:
    defaults = dict(
        id="ses-1",
        student_id="sp-1",
        course_id="course-1",
        current_lesson_id=None,
        current_concept_id=None,
        state=SessionState.ACTIVE,
        context={},
        started_at=datetime.now(timezone.utc),
        last_activity_at=datetime.now(timezone.utc),
        completed_at=None,
    )
    defaults.update(overrides)
    return TeachingSession(**defaults)


class TestSessionService:
    @pytest.mark.asyncio
    async def test_start_session(
        self, mock_session, mock_student_profile, mock_course
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_active_by_student_and_course = AsyncMock(return_value=None)
        service.course_repo.get = AsyncMock(return_value=mock_course)
        service.session_repo.create = AsyncMock(return_value=_make_session())

        session = await service.start_session(
            user_id="user-1", course_id="course-1"
        )
        assert session.id == "ses-1"
        assert session.state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_start_session_no_profile(self, mock_session) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.start_session(user_id="user-1", course_id="course-1")

    @pytest.mark.asyncio
    async def test_start_session_duplicate(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_active_by_student_and_course = AsyncMock(
            return_value=_make_session()
        )

        with pytest.raises(ConflictException):
            await service.start_session(user_id="user-1", course_id="course-1")

    @pytest.mark.asyncio
    async def test_start_session_course_not_found(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_active_by_student_and_course = AsyncMock(return_value=None)
        service.course_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.start_session(user_id="user-1", course_id="course-1")

    @pytest.mark.asyncio
    async def test_start_session_with_lesson_and_concept(
        self, mock_session, mock_student_profile, mock_course, mock_lesson, mock_concept
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_active_by_student_and_course = AsyncMock(return_value=None)
        service.course_repo.get = AsyncMock(return_value=mock_course)
        service.lesson_repo.get = AsyncMock(return_value=mock_lesson)
        service.concept_repo.get = AsyncMock(return_value=mock_concept)
        service.session_repo.create = AsyncMock(
            return_value=_make_session(
                current_lesson_id="lsn-1",
                current_concept_id="con-1",
            )
        )

        session = await service.start_session(
            user_id="user-1",
            course_id="course-1",
            lesson_id="lsn-1",
            concept_id="con-1",
        )
        assert session.current_lesson_id == "lsn-1"
        assert session.current_concept_id == "con-1"

    @pytest.mark.asyncio
    async def test_start_session_lesson_not_found(
        self, mock_session, mock_student_profile, mock_course
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_active_by_student_and_course = AsyncMock(return_value=None)
        service.course_repo.get = AsyncMock(return_value=mock_course)
        service.lesson_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.start_session(
                user_id="user-1", course_id="course-1", lesson_id="bad-lsn"
            )

    @pytest.mark.asyncio
    async def test_resume_session(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_latest_resumable = AsyncMock(
            return_value=_make_session(state=SessionState.PAUSED)
        )
        mock_session.refresh = AsyncMock(
            return_value=_make_session(state=SessionState.ACTIVE)
        )

        session = await service.resume_session(user_id="user-1")
        assert session.state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_resume_session_none_found(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_latest_resumable = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.resume_session(user_id="user-1")

    @pytest.mark.asyncio
    async def test_pause_session(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.get = AsyncMock(return_value=_make_session())
        mock_session.refresh = AsyncMock(
            return_value=_make_session(state=SessionState.PAUSED)
        )

        session = await service.pause_session("ses-1", "user-1")
        assert session.state == SessionState.PAUSED

    @pytest.mark.asyncio
    async def test_pause_session_not_found(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.pause_session("bad-id", "user-1")

    @pytest.mark.asyncio
    async def test_pause_session_not_active(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.get = AsyncMock(
            return_value=_make_session(state=SessionState.PAUSED)
        )

        with pytest.raises(ValidationException):
            await service.pause_session("ses-1", "user-1")

    @pytest.mark.asyncio
    async def test_end_session(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.get = AsyncMock(return_value=_make_session())
        mock_session.refresh = AsyncMock(
            return_value=_make_session(
                state=SessionState.COMPLETED,
                completed_at=datetime.now(timezone.utc),
            )
        )

        session = await service.end_session("ses-1", "user-1")
        assert session.state == SessionState.COMPLETED
        assert session.completed_at is not None

    @pytest.mark.asyncio
    async def test_end_session_already_ended(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.get = AsyncMock(
            return_value=_make_session(state=SessionState.COMPLETED)
        )

        with pytest.raises(ValidationException):
            await service.end_session("ses-1", "user-1")

    @pytest.mark.asyncio
    async def test_end_session_wrong_owner(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        wrong_session = _make_session(student_id="other-sp")
        service.session_repo.get = AsyncMock(return_value=wrong_session)

        with pytest.raises(NotFoundException):
            await service.end_session("ses-1", "user-1")

    @pytest.mark.asyncio
    async def test_get_session_history(
        self, mock_session, mock_student_profile
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.session_repo.find_by_student = AsyncMock(
            return_value=([_make_session()], 1)
        )

        sessions, total = await service.get_session_history("user-1")
        assert len(sessions) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_session_history_admin(
        self, mock_session
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get = AsyncMock(
            return_value=MagicMock(id="sp-2")
        )
        service.session_repo.find_by_student = AsyncMock(
            return_value=([_make_session(student_id="sp-2")], 1)
        )

        sessions, total = await service.get_session_history(
            user_id="admin-1", is_admin=True, student_id="sp-2"
        )
        assert len(sessions) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_session_history_admin_student_not_found(
        self, mock_session
    ) -> None:
        service = SessionService(mock_session)
        service.student_profile_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_session_history(
                user_id="admin-1", is_admin=True, student_id="bad-id"
            )

    def test_session_context(self) -> None:
        session = _make_session(
            current_lesson_id="lsn-1",
            current_concept_id="con-1",
        )
        service = SessionService(MagicMock())
        ctx = service.get_context(session)
        assert ctx.session_id == "ses-1"
        assert ctx.current_lesson_id == "lsn-1"
        assert ctx.current_concept_id == "con-1"
        assert ctx.state == SessionState.ACTIVE
