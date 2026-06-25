from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.common.exceptions import ForbiddenException, NotFoundException
from app.common.types import LessonProgressStatus, UserRole
from app.teacher.repository import TeacherCourseAssignmentRepository, TeacherStudentAssignmentRepository
from app.teacher.schemas import (
    MasteryConceptItem,
    MasterySummaryResponse,
    ProgressSummaryResponse,
    SessionItem,
    TeacherCourseResponse,
    TeacherDashboardResponse,
    TeacherStudentResponse,
)
from app.teacher.service import TeacherService
from app.users.models import User


def _make_user(role: UserRole = UserRole.TEACHER, user_id: str = "teacher-1") -> User:
    return User(
        id=user_id,
        email="teacher@test.com",
        password_hash="hash",
        full_name="Test Teacher",
        role=role,
        is_active=True,
    )


def _make_student_profile(**overrides) -> Mock:
    profile = Mock(spec=["id", "user_id", "grade_level", "current_streak_days"])
    profile.id = "sp-1"
    profile.user_id = "user-student-1"
    profile.grade_level = "Grade 5"
    profile.current_streak_days = 3
    for k, v in overrides.items():
        setattr(profile, k, v)
    return profile


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# TeacherService
# ---------------------------------------------------------------------------


class TestTeacherService:
    @pytest.mark.asyncio
    async def test_list_students_as_admin(self, mock_session) -> None:
        service = TeacherService(mock_session)
        admin_user = _make_user(UserRole.ADMIN)

        profile = _make_student_profile()
        service.student_profile_repo.find = AsyncMock(return_value=[profile])

        user = Mock(spec=User)
        user.id = "user-student-1"
        user.full_name = "Student Name"
        user.email = "student@test.com"
        service.user_repo.get = AsyncMock(return_value=user)

        enrollment = MagicMock()
        enrollment.id = "enr-1"
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[enrollment])

        record = MagicMock()
        record.mastery_level = 0.85
        service.mastery_repo.find_by_student = AsyncMock(return_value=[record])

        session_stmt = MagicMock()
        session_stmt.unique.return_value.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=session_stmt)

        result = await service.list_students(admin_user)

        assert len(result) == 1
        assert isinstance(result[0], TeacherStudentResponse)
        assert result[0].student_id == "sp-1"
        assert result[0].full_name == "Student Name"
        assert result[0].active_courses == 1
        assert result[0].overall_mastery_avg == 0.85

    @pytest.mark.asyncio
    async def test_list_students_as_teacher(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()

        assignment = MagicMock()
        assignment.student = _make_student_profile()
        assignment.assigned_at = datetime.now(timezone.utc)
        service.student_assign_repo.find_by_teacher = AsyncMock(return_value=[assignment])

        user = Mock(spec=User)
        user.id = "user-student-1"
        user.full_name = "Student Name"
        user.email = "student@test.com"
        service.user_repo.get = AsyncMock(return_value=user)

        service.enrollment_repo.find_by_student = AsyncMock(return_value=[])
        service.mastery_repo.find_by_student = AsyncMock(return_value=[])

        session_stmt = MagicMock()
        session_stmt.unique.return_value.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=session_stmt)

        result = await service.list_students(teacher_user)

        assert len(result) == 1
        assert result[0].overall_mastery_avg == 0.0
        assert result[0].assigned_at is not None

    @pytest.mark.asyncio
    async def test_list_students_empty(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()
        service.student_assign_repo.find_by_teacher = AsyncMock(return_value=[])
        result = await service.list_students(teacher_user)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_student_progress_success(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()
        profile = _make_student_profile()

        service._verify_teacher_access = AsyncMock(return_value=profile)

        progresses = [
            MagicMock(status=LessonProgressStatus.COMPLETED),
            MagicMock(status=LessonProgressStatus.COMPLETED),
            MagicMock(status=LessonProgressStatus.IN_PROGRESS),
            MagicMock(status=LessonProgressStatus.NOT_STARTED),
        ]
        service.progress_repo.find_by_student = AsyncMock(return_value=progresses)

        result = await service.get_student_progress(teacher_user, "sp-1")

        assert isinstance(result, ProgressSummaryResponse)
        assert result.total_lessons == 4
        assert result.completed_lessons == 2
        assert result.in_progress_lessons == 1
        assert result.completion_percentage == 50.0

    @pytest.mark.asyncio
    async def test_get_student_progress_no_lessons(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()
        profile = _make_student_profile()

        service._verify_teacher_access = AsyncMock(return_value=profile)
        service.progress_repo.find_by_student = AsyncMock(return_value=[])

        result = await service.get_student_progress(teacher_user, "sp-1")

        assert result.total_lessons == 0
        assert result.completion_percentage == 0.0

    @pytest.mark.asyncio
    async def test_get_student_progress_forbidden(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()

        service._verify_teacher_access = AsyncMock(
            side_effect=ForbiddenException("You are not assigned to this student")
        )

        with pytest.raises(ForbiddenException):
            await service.get_student_progress(teacher_user, "sp-unknown")

    @pytest.mark.asyncio
    async def test_get_student_progress_not_found(self, mock_session) -> None:
        service = TeacherService(mock_session)
        admin_user = _make_user(UserRole.ADMIN)

        service._verify_teacher_access = AsyncMock(
            side_effect=NotFoundException("Student not found")
        )

        with pytest.raises(NotFoundException):
            await service.get_student_progress(admin_user, "nonexistent")

    @pytest.mark.asyncio
    async def test_get_student_mastery_success(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()
        profile = _make_student_profile()

        service._verify_teacher_access = AsyncMock(return_value=profile)

        concept = MagicMock()
        concept.title = "Algebra"

        records = []
        for i, level in enumerate([0.9, 0.5, 0.0]):
            r = MagicMock()
            r.concept_id = f"con-{i}"
            r.concept = concept
            r.mastery_level = level
            r.total_attempts = i + 1
            r.consecutive_correct = i
            r.last_attempted_at = datetime.now(timezone.utc)
            records.append(r)

        service.mastery_repo.find_by_student = AsyncMock(return_value=records)

        result = await service.get_student_mastery(teacher_user, "sp-1")

        assert isinstance(result, MasterySummaryResponse)
        assert result.total_concepts == 3
        assert result.mastered_concepts == 1
        assert result.in_progress_concepts == 1
        assert result.not_started_concepts == 1
        assert result.average_mastery == pytest.approx(0.4667, 0.01)

    @pytest.mark.asyncio
    async def test_get_student_mastery_empty(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()
        profile = _make_student_profile()

        service._verify_teacher_access = AsyncMock(return_value=profile)
        service.mastery_repo.find_by_student = AsyncMock(return_value=[])

        result = await service.get_student_mastery(teacher_user, "sp-1")

        assert result.total_concepts == 0
        assert result.average_mastery == 0.0
        assert result.concepts == []

    @pytest.mark.asyncio
    async def test_get_dashboard(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()

        profile = _make_student_profile()
        user = Mock(spec=User)
        user.id = "user-student-1"
        user.full_name = "Student Name"
        user.email = "student@test.com"

        assignment = MagicMock()
        assignment.student = profile
        assignment.assigned_at = datetime.now(timezone.utc)

        service.student_assign_repo.find_by_teacher = AsyncMock(return_value=[assignment])
        service.user_repo.get = AsyncMock(return_value=user)
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[])
        service.mastery_repo.find_by_student = AsyncMock(return_value=[])

        now = datetime.now(timezone.utc)
        session_stmt = MagicMock()
        session_stmt.unique.return_value.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=session_stmt)

        course_assign = MagicMock()
        course_assign.course = MagicMock()
        course_assign.course.id = "course-1"
        course_assign.course.title = "Math 101"
        course_assign.course.code = "MATH101"
        course_assign.role = "instructor"
        course_assign.assigned_at = now
        service.course_assign_repo.find_by_teacher = AsyncMock(return_value=[course_assign])

        # Make get_student_sessions return empty
        service.get_student_sessions = AsyncMock(return_value=([], 0))

        result = await service.get_dashboard(teacher_user)

        assert isinstance(result, TeacherDashboardResponse)
        assert result.total_students == 1
        assert result.total_courses == 1
        assert len(result.students) == 1
        assert len(result.recent_sessions) == 0

    @pytest.mark.asyncio
    async def test_get_dashboard_empty(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = _make_user()

        service.student_assign_repo.find_by_teacher = AsyncMock(return_value=[])
        service.course_assign_repo.find_by_teacher = AsyncMock(return_value=[])

        result = await service.get_dashboard(teacher_user)

        assert result.total_students == 0
        assert result.total_courses == 0
        assert result.students == []
        assert result.recent_sessions == []


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------


class TestTeacherStudentAssignmentRepository:
    @pytest.mark.asyncio
    async def test_find_by_teacher(self) -> None:
        session = MagicMock()
        repo = TeacherStudentAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = [MagicMock()]
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_teacher("teacher-1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_find_by_teacher_empty(self) -> None:
        session = MagicMock()
        repo = TeacherStudentAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_teacher("teacher-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_find_by_student(self) -> None:
        session = MagicMock()
        repo = TeacherStudentAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = [MagicMock()]
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_student("sp-1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_find_by_teacher_and_student_found(self) -> None:
        session = MagicMock()
        repo = TeacherStudentAssignmentRepository(session)

        expected = MagicMock()
        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalar_one_or_none.return_value = expected
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_teacher_and_student("teacher-1", "sp-1")
        assert result is expected

    @pytest.mark.asyncio
    async def test_find_by_teacher_and_student_not_found(self) -> None:
        session = MagicMock()
        repo = TeacherStudentAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_teacher_and_student("teacher-1", "sp-unknown")
        assert result is None


class TestTeacherCourseAssignmentRepository:
    @pytest.mark.asyncio
    async def test_find_by_teacher(self) -> None:
        session = MagicMock()
        repo = TeacherCourseAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = [MagicMock()]
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_teacher("teacher-1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_find_by_teacher_empty(self) -> None:
        session = MagicMock()
        repo = TeacherCourseAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_teacher("teacher-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_find_by_course(self) -> None:
        session = MagicMock()
        repo = TeacherCourseAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = [MagicMock()]
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_course("course-1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_find_by_course_empty(self) -> None:
        session = MagicMock()
        repo = TeacherCourseAssignmentRepository(session)

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=stmt_result)

        result = await repo.find_by_course("course-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_create(self) -> None:
        session = MagicMock()
        repo = TeacherCourseAssignmentRepository(session)
        session.add = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()

        mock_instance = MagicMock()
        mock_instance.id = "ca-1"

        with patch.object(repo, "model") as mock_model:
            mock_model.return_value = mock_instance
            result = await repo.create(
                teacher_id="teacher-1",
                course_id="course-1",
                role="instructor",
            )

            assert result.id == "ca-1"
            session.add.assert_called_once_with(mock_instance)
