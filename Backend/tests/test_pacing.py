from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import NotFoundException, ValidationException
from app.common.types import PaceStatus
from app.enrollment.models import CourseSchedule
from app.pacing.service import PacingService


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
def mock_enrollment() -> MagicMock:
    enr = MagicMock()
    enr.id = "enr-1"
    enr.student_id = "sp-1"
    enr.course_id = "course-1"
    return enr


@pytest.fixture
def mock_course() -> MagicMock:
    course = MagicMock()
    course.id = "course-1"
    course.title = "Test Course"
    course.default_deadline_days = 90
    course.modules = []
    return course


def _make_schedule(**overrides) -> CourseSchedule:
    defaults = dict(
        id="sched-1",
        enrollment_id="enr-1",
        target_lessons_per_week=3,
        current_week=1,
        pace_status=PaceStatus.ON_TRACK,
        last_pacing_adjustment_at=None,
        milestones=[],
    )
    defaults.update(overrides)
    return CourseSchedule(**defaults)


# ---------------------------------------------------------------------------
# PacingService
# ---------------------------------------------------------------------------

class TestPacingService:
    @pytest.mark.asyncio
    async def test_get_pacing_status(
        self, mock_session, mock_student_profile, mock_enrollment, mock_course
    ) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[mock_enrollment])
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=_make_schedule())
        service.course_repo.get = AsyncMock(return_value=mock_course)

        statuses = await service.get_pacing_status("user-1")
        assert len(statuses) == 1
        assert statuses[0]["pace_status"] == PaceStatus.ON_TRACK

    @pytest.mark.asyncio
    async def test_get_pacing_status_no_schedule(
        self, mock_session, mock_student_profile, mock_enrollment
    ) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[mock_enrollment])
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=None)

        statuses = await service.get_pacing_status("user-1")
        assert len(statuses) == 0

    @pytest.mark.asyncio
    async def test_update_pacing_status(
        self, mock_session, mock_student_profile, mock_enrollment
    ) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.get = AsyncMock(return_value=mock_enrollment)
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=_make_schedule())
        service.schedule_repo.update = AsyncMock(
            return_value=_make_schedule(
                pace_status=PaceStatus.BEHIND,
                last_pacing_adjustment_at=datetime.now(timezone.utc),
            )
        )

        schedule = await service.update_pacing_status(
            "user-1", "enr-1", PaceStatus.BEHIND
        )
        assert schedule.pace_status == PaceStatus.BEHIND

    @pytest.mark.asyncio
    async def test_update_pacing_status_no_schedule(
        self, mock_session, mock_student_profile, mock_enrollment
    ) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.get = AsyncMock(return_value=mock_enrollment)
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.update_pacing_status("user-1", "enr-1", PaceStatus.BEHIND)

    @pytest.mark.asyncio
    async def test_update_pacing_status_wrong_enrollment(
        self, mock_session, mock_student_profile
    ) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)

        wrong_enr = MagicMock()
        wrong_enr.id = "enr-2"
        wrong_enr.student_id = "other-sp"
        service.enrollment_repo.get = AsyncMock(return_value=wrong_enr)

        with pytest.raises(NotFoundException):
            await service.update_pacing_status("user-1", "enr-2", PaceStatus.BEHIND)

    @pytest.mark.asyncio
    async def test_generate_schedule(
        self, mock_session, mock_student_profile, mock_enrollment, mock_course
    ) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.get = AsyncMock(return_value=mock_enrollment)
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=None)
        service.course_repo.get = AsyncMock(return_value=mock_course)
        service.schedule_repo.create = AsyncMock(return_value=_make_schedule())

        schedule = await service.generate_schedule("enr-1", "user-1")
        assert schedule.pace_status == PaceStatus.ON_TRACK

    @pytest.mark.asyncio
    async def test_generate_schedule_already_exists(
        self, mock_session, mock_student_profile, mock_enrollment
    ) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.get = AsyncMock(return_value=mock_enrollment)
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=_make_schedule())

        with pytest.raises(ValidationException):
            await service.generate_schedule("enr-1", "user-1")

    @pytest.mark.asyncio
    async def test_no_student_profile(self, mock_session) -> None:
        service = PacingService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_pacing_status("user-1")
