from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.service import AnalyticsService
from app.analytics.schemas import (
    AssessmentAnalytics,
    CourseProgressAnalytics,
    StudentProgressAnalytics,
    SystemOverview,
)
from app.common.types import EnrollmentStatus, LessonProgressStatus, UserRole


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


class TestAnalyticsIntegrationFlow:
    """End-to-end analytics flow test with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_full_analytics_flow(self, mock_session) -> None:
        service = AnalyticsService(mock_session)
        now = datetime.now(timezone.utc)

        # Step 1: Assessment analytics
        attempt1 = MagicMock()
        attempt1.score = 0.85
        attempt1.passed = True
        attempt1.started_at = now - timedelta(seconds=300)
        attempt1.completed_at = now

        attempt2 = MagicMock()
        attempt2.score = 0.45
        attempt2.passed = False
        attempt2.started_at = now - timedelta(seconds=600)
        attempt2.completed_at = now

        stmt_result = MagicMock()
        stmt_result.scalars.return_value.all.return_value = [attempt1, attempt2]
        mock_session.execute = AsyncMock(return_value=stmt_result)

        assessment_analytics = await service.get_assessment_analytics("course-1")
        assert isinstance(assessment_analytics, AssessmentAnalytics)
        assert assessment_analytics.total_attempts == 2
        assert assessment_analytics.pass_count == 1
        assert assessment_analytics.fail_count == 1
        assert assessment_analytics.pass_rate == 50.0

        # Step 2: Student progress analytics
        lp1 = MagicMock()
        lp1.status = LessonProgressStatus.COMPLETED
        lp1.time_spent_seconds = 600
        lp1.started_at = now - timedelta(days=1)

        lp2 = MagicMock()
        lp2.status = LessonProgressStatus.COMPLETED
        lp2.time_spent_seconds = 300
        lp2.started_at = now - timedelta(days=2)

        lp3 = MagicMock()
        lp3.status = LessonProgressStatus.IN_PROGRESS
        lp3.time_spent_seconds = 120
        lp3.started_at = now - timedelta(days=14)

        progress_result = MagicMock()
        progress_result.scalars.return_value.all.return_value = [lp1, lp2, lp3]

        avg_result = MagicMock()
        avg_result.scalar.return_value = 0.72

        mock_session.execute = AsyncMock(side_effect=[progress_result, avg_result])

        student_analytics = await service.get_student_progress_analytics("sp-1")
        assert isinstance(student_analytics, StudentProgressAnalytics)
        assert student_analytics.total_lessons == 3
        assert student_analytics.completed_lessons == 2
        assert student_analytics.completion_rate == 66.67
        assert student_analytics.average_mastery == 0.72
        assert student_analytics.total_time_spent_minutes == 17.0
        assert student_analytics.lessons_overdue == 1

        # Step 3: Course analytics
        scalar_results = [5, 3, 0.65, 0.72, 10, 0.78]
        call_count = 0

        async def mock_scalar(stmt):
            nonlocal call_count
            val = scalar_results[call_count]
            call_count += 1
            return val

        mock_session.scalar = AsyncMock(side_effect=mock_scalar)

        course_analytics = await service.get_course_analytics("course-1")
        assert isinstance(course_analytics, CourseProgressAnalytics)
        assert course_analytics.total_students == 5
        assert course_analytics.active_students == 3
        assert course_analytics.average_completion_rate == 0.65
        assert course_analytics.average_mastery_score == 0.72
        assert course_analytics.total_assessments_taken == 10
        assert course_analytics.average_assessment_score == 0.78

        # Step 4: System overview
        user_count_result = MagicMock()
        user_count_result.all.return_value = [
            (UserRole.STUDENT, 50),
            (UserRole.TEACHER, 5),
            (UserRole.ADMIN, 1),
        ]
        mock_session.execute = AsyncMock(return_value=user_count_result)

        scalar_values = [8, 80, 200, 15]
        scalar_call_count = 0

        async def mock_scalar2(stmt):
            nonlocal scalar_call_count
            val = scalar_values[scalar_call_count]
            scalar_call_count += 1
            return val

        mock_session.scalar = AsyncMock(side_effect=mock_scalar2)

        overview = await service.get_system_overview()
        assert isinstance(overview, SystemOverview)
        assert overview.total_users == 56
        assert overview.total_students == 50
        assert overview.total_teachers == 5
        assert overview.total_courses == 8
        assert overview.total_enrollments == 80
        assert overview.total_assessment_attempts == 200
        assert overview.active_sessions_today == 15

    @pytest.mark.asyncio
    async def test_analytics_empty_data(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        stmt_result = MagicMock()
        stmt_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=stmt_result)

        assessment_analytics = await service.get_assessment_analytics("course-empty")
        assert assessment_analytics.total_attempts == 0
        assert assessment_analytics.average_score == 0.0

        avg_result = MagicMock()
        avg_result.scalar.return_value = None
        mock_session.execute = AsyncMock(side_effect=[stmt_result, avg_result])

        student_analytics = await service.get_student_progress_analytics("sp-empty")
        assert student_analytics.total_lessons == 0
        assert student_analytics.completion_rate == 0.0

        mock_session.scalar = AsyncMock(return_value=0)

        course_analytics = await service.get_course_analytics("course-empty")
        assert course_analytics.total_students == 0

        user_count_result = MagicMock()
        user_count_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=user_count_result)
        mock_session.scalar = AsyncMock(return_value=0)

        overview = await service.get_system_overview()
        assert overview.total_users == 0
        assert overview.total_courses == 0
