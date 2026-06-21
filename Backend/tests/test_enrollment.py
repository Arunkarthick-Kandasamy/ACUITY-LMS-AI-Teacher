from __future__ import annotations

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import ConflictException, NotFoundException, ValidationException
from app.common.types import EnrollmentStatus, PaceStatus
from app.enrollment.models import CourseSchedule, StudentCourseEnrollment
from app.enrollment.service import EnrollmentService


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_course() -> MagicMock:
    course = MagicMock()
    course.id = "course-1"
    course.code = "CS101"
    course.title = "Intro to CS"
    course.is_published = True
    course.default_deadline_days = 90
    course.modules = []
    return course


@pytest.fixture
def mock_student_profile() -> MagicMock:
    profile = MagicMock()
    profile.id = "sp-1"
    profile.user_id = "user-1"
    return profile


def _make_enrollment(**overrides) -> StudentCourseEnrollment:
    defaults = dict(
        id="enr-1",
        student_id="sp-1",
        course_id="course-1",
        status=EnrollmentStatus.ACTIVE,
        enrolled_at=datetime.now(timezone.utc),
        started_at=datetime.now(timezone.utc),
        target_completion_date=date.today(),
        completed_at=None,
        current_concept_id=None,
    )
    defaults.update(overrides)
    return StudentCourseEnrollment(**defaults)


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
# EnrollmentService
# ---------------------------------------------------------------------------

class TestEnrollmentService:
    @pytest.mark.asyncio
    async def test_enroll_success(self, mock_session, mock_course, mock_student_profile) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)

        from app.curriculum.repository import CourseRepository
        original_get = CourseRepository.get
        CourseRepository.get = AsyncMock(return_value=mock_course)

        service.enrollment_repo.find_active_by_student_and_course = AsyncMock(return_value=None)
        service.enrollment_repo.create = AsyncMock(return_value=_make_enrollment())
        service.schedule_repo.create = AsyncMock(return_value=_make_schedule())

        enrollment = await service.enroll(user_id="user-1", course_id="course-1")
        assert enrollment.id == "enr-1"
        assert enrollment.status == EnrollmentStatus.ACTIVE

        CourseRepository.get = original_get

    @pytest.mark.asyncio
    async def test_enroll_no_student_profile(self, mock_session) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=None)

        with pytest.raises(ValidationException):
            await service.enroll(user_id="user-1", course_id="course-1")

    @pytest.mark.asyncio
    async def test_enroll_course_not_published(self, mock_session, mock_student_profile) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)

        course = MagicMock()
        course.id = "course-1"
        course.is_published = False

        from app.curriculum.repository import CourseRepository
        original_get = CourseRepository.get
        CourseRepository.get = AsyncMock(return_value=course)

        with pytest.raises(ValidationException):
            await service.enroll(user_id="user-1", course_id="course-1")

        CourseRepository.get = original_get

    @pytest.mark.asyncio
    async def test_enroll_duplicate(self, mock_session, mock_course, mock_student_profile) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)

        from app.curriculum.repository import CourseRepository
        original_get = CourseRepository.get
        CourseRepository.get = AsyncMock(return_value=mock_course)

        service.enrollment_repo.find_active_by_student_and_course = AsyncMock(
            return_value=_make_enrollment()
        )

        with pytest.raises(ConflictException):
            await service.enroll(user_id="user-1", course_id="course-1")

        CourseRepository.get = original_get

    @pytest.mark.asyncio
    async def test_list_enrollments(self, mock_session, mock_student_profile) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[_make_enrollment()])

        enrollments = await service.list_enrollments(user_id="user-1")
        assert len(enrollments) == 1
        assert enrollments[0].id == "enr-1"

    @pytest.mark.asyncio
    async def test_get_enrollment_success(self, mock_session, mock_student_profile) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.get = AsyncMock(return_value=_make_enrollment())

        enrollment = await service.get_enrollment(
            "enr-1", user_id="user-1"
        )
        assert enrollment.id == "enr-1"

    @pytest.mark.asyncio
    async def test_get_enrollment_not_found(self, mock_session) -> None:
        service = EnrollmentService(mock_session)
        service.enrollment_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_enrollment("nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_get_enrollment_wrong_student(self, mock_session, mock_student_profile) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.enrollment_repo.get = AsyncMock(return_value=_make_enrollment(student_id="other-sp"))

        with pytest.raises(NotFoundException):
            await service.get_enrollment("enr-1", user_id="user-1")

    @pytest.mark.asyncio
    async def test_admin_list_with_student_id(self, mock_session) -> None:
        service = EnrollmentService(mock_session)
        service.student_profile_repo.get = AsyncMock(return_value=MagicMock(id="sp-2"))
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[_make_enrollment()])

        enrollments = await service.list_enrollments(
            user_id="admin-1", is_admin=True, student_id="sp-2"
        )
        assert len(enrollments) == 1
