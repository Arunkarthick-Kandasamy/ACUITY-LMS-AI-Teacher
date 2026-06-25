from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.common.types import LessonProgressStatus, UserRole
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


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


class TestTeacherIntegrationFlow:
    """End-to-end teacher flow test with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_full_teacher_flow(self, mock_session) -> None:
        service = TeacherService(mock_session)
        now = datetime.now(timezone.utc)

        profile = MagicMock()
        profile.id = "sp-1"
        profile.user_id = "user-student-1"
        profile.grade_level = "Grade 5"
        profile.current_streak_days = 3

        teacher_user = User(
            id="teacher-1",
            email="teacher@test.com",
            password_hash="hash",
            full_name="Test Teacher",
            role=UserRole.TEACHER,
            is_active=True,
        )

        # Step 1: Assign student to teacher via assignment
        assignment = MagicMock()
        assignment.student = profile
        assignment.assigned_at = now
        service.student_assign_repo.find_by_teacher = AsyncMock(return_value=[assignment])

        student_user = Mock(spec=User)
        student_user.id = "user-student-1"
        student_user.full_name = "Student One"
        student_user.email = "student@test.com"
        service.user_repo.get = AsyncMock(return_value=student_user)

        enrollment = MagicMock()
        enrollment.id = "enr-1"
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[enrollment])

        record = MagicMock()
        record.mastery_level = 0.85
        service.mastery_repo.find_by_student = AsyncMock(return_value=[record])

        session_stmt = MagicMock()
        session_stmt.unique.return_value.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=session_stmt)

        # Step 2: List students
        students = await service.list_students(teacher_user)
        assert len(students) == 1
        assert students[0].full_name == "Student One"
        assert students[0].active_courses == 1
        assert students[0].overall_mastery_avg == 0.85
        assert students[0].grade_level == "Grade 5"

        # Step 3: Get student progress
        service._verify_teacher_access = AsyncMock(return_value=profile)

        progresses = [
            MagicMock(status=LessonProgressStatus.COMPLETED),
            MagicMock(status=LessonProgressStatus.COMPLETED),
            MagicMock(status=LessonProgressStatus.IN_PROGRESS),
        ]
        service.progress_repo.find_by_student = AsyncMock(return_value=progresses)

        progress = await service.get_student_progress(teacher_user, "sp-1")
        assert isinstance(progress, ProgressSummaryResponse)
        assert progress.total_lessons == 3
        assert progress.completed_lessons == 2
        assert progress.completion_percentage == 66.7

        # Step 4: Get student mastery
        concept = MagicMock()
        concept.title = "Algebra"

        mastery_records = []
        for i, level in enumerate([0.9, 0.6, 0.0]):
            r = MagicMock()
            r.concept_id = f"con-{i}"
            r.concept = concept
            r.mastery_level = level
            r.total_attempts = i + 1
            r.consecutive_correct = i
            r.last_attempted_at = now
            mastery_records.append(r)

        service.mastery_repo.find_by_student = AsyncMock(return_value=mastery_records)

        mastery = await service.get_student_mastery(teacher_user, "sp-1")
        assert isinstance(mastery, MasterySummaryResponse)
        assert mastery.total_concepts == 3
        assert mastery.mastered_concepts == 1
        assert mastery.in_progress_concepts == 1
        assert mastery.not_started_concepts == 1
        assert len(mastery.concepts) == 3

        # Step 5: Get dashboard
        service.student_assign_repo.find_by_teacher = AsyncMock(return_value=[assignment])
        service.user_repo.get = AsyncMock(return_value=student_user)
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[enrollment])
        service.mastery_repo.find_by_student = AsyncMock(return_value=[record])
        mock_session.execute = AsyncMock(return_value=session_stmt)

        course_assign = MagicMock()
        course_assign.course = MagicMock()
        course_assign.course.id = "course-1"
        course_assign.course.title = "Math 101"
        course_assign.course.code = "MATH101"
        course_assign.role = "instructor"
        course_assign.assigned_at = now
        service.course_assign_repo.find_by_teacher = AsyncMock(return_value=[course_assign])

        service.get_student_sessions = AsyncMock(return_value=([], 0))

        dashboard = await service.get_dashboard(teacher_user)
        assert isinstance(dashboard, TeacherDashboardResponse)
        assert dashboard.total_students == 1
        assert dashboard.total_courses == 1
        assert dashboard.recent_sessions == []

        # Step 6: Unauthorized access - teacher not assigned to student
        service._verify_teacher_access = AsyncMock(
            side_effect=__import__("app.common.exceptions", fromlist=["ForbiddenException"]).ForbiddenException(
                "You are not assigned to this student"
            )
        )

        with pytest.raises(Exception):
            await service.get_student_progress(teacher_user, "sp-unknown")

    @pytest.mark.asyncio
    async def test_teacher_flow_empty_data(self, mock_session) -> None:
        service = TeacherService(mock_session)
        teacher_user = User(
            id="teacher-1",
            email="teacher@test.com",
            password_hash="hash",
            full_name="Test Teacher",
            role=UserRole.TEACHER,
            is_active=True,
        )

        service.student_assign_repo.find_by_teacher = AsyncMock(return_value=[])
        service.course_assign_repo.find_by_teacher = AsyncMock(return_value=[])

        dashboard = await service.get_dashboard(teacher_user)
        assert dashboard.total_students == 0
        assert dashboard.total_courses == 0
        assert dashboard.students == []

        students = await service.list_students(teacher_user)
        assert students == []

    @pytest.mark.asyncio
    async def test_teacher_admin_access(self, mock_session) -> None:
        service = TeacherService(mock_session)
        admin_user = User(
            id="admin-1",
            email="admin@test.com",
            password_hash="hash",
            full_name="Admin",
            role=UserRole.ADMIN,
            is_active=True,
        )

        profile = MagicMock()
        profile.id = "sp-1"
        profile.user_id = "user-student-1"
        profile.grade_level = "Grade 5"
        profile.current_streak_days = 3
        service.student_profile_repo.find = AsyncMock(return_value=[profile])

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

        students = await service.list_students(admin_user)
        assert len(students) == 1
        assert students[0].student_id == "sp-1"
