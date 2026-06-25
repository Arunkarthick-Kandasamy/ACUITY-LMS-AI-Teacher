from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, Mock

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


# ---------------------------------------------------------------------------
# AnalyticsService
# ---------------------------------------------------------------------------


class TestAnalyticsService:
    @pytest.mark.asyncio
    async def test_get_assessment_analytics_with_data(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        now = datetime.now(timezone.utc)
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

        result = await service.get_assessment_analytics("course-1")

        assert isinstance(result, AssessmentAnalytics)
        assert result.total_attempts == 2
        assert result.pass_rate == 50.0
        assert result.pass_count == 1
        assert result.fail_count == 1
        assert result.average_score == 0.65
        assert result.avg_time_spent_seconds is not None

    @pytest.mark.asyncio
    async def test_get_assessment_analytics_empty(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        stmt_result = MagicMock()
        stmt_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=stmt_result)

        result = await service.get_assessment_analytics("course-empty")

        assert result.total_attempts == 0
        assert result.average_score == 0.0
        assert result.pass_rate == 0.0
        assert result.avg_time_spent_seconds is None

    @pytest.mark.asyncio
    async def test_get_assessment_analytics_no_times(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        attempt1 = MagicMock()
        attempt1.score = 0.9
        attempt1.passed = True
        attempt1.started_at = None
        attempt1.completed_at = None

        attempt2 = MagicMock()
        attempt2.score = 0.5
        attempt2.passed = False
        attempt2.started_at = None
        attempt2.completed_at = None

        stmt_result = MagicMock()
        stmt_result.scalars.return_value.all.return_value = [attempt1, attempt2]
        mock_session.execute = AsyncMock(return_value=stmt_result)

        result = await service.get_assessment_analytics("course-1")

        assert result.total_attempts == 2
        assert result.avg_time_spent_seconds is None

    @pytest.mark.asyncio
    async def test_get_student_progress_analytics(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        now = datetime.now(timezone.utc)
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

        stmt_result = MagicMock()
        stmt_result.scalars.return_value.all.return_value = [lp1, lp2, lp3]
        mock_session.execute = AsyncMock(return_value=stmt_result)

        avg_result = MagicMock()
        avg_result.scalar.return_value = 0.75
        mock_session.execute = AsyncMock(side_effect=[stmt_result, avg_result])

        result = await service.get_student_progress_analytics("sp-1")

        assert isinstance(result, StudentProgressAnalytics)
        assert result.total_lessons == 3
        assert result.completed_lessons == 2
        assert result.completion_rate == 66.67
        assert result.average_mastery == 0.75
        assert result.total_time_spent_minutes == 17.0
        assert result.lessons_overdue == 1

    @pytest.mark.asyncio
    async def test_get_student_progress_analytics_empty(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        stmt_result = MagicMock()
        stmt_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=stmt_result)

        avg_result = MagicMock()
        avg_result.scalar.return_value = None
        mock_session.execute = AsyncMock(side_effect=[stmt_result, avg_result])

        result = await service.get_student_progress_analytics("sp-empty")

        assert result.total_lessons == 0
        assert result.completion_rate == 0.0
        assert result.average_mastery == 0.0
        assert result.total_time_spent_minutes == 0.0
        assert result.lessons_overdue == 0

    @pytest.mark.asyncio
    async def test_get_course_analytics(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        scalar_results = [5, 3, 0.65, 0.72, 10, 0.78]
        call_count = 0

        async def mock_scalar(stmt):
            nonlocal call_count
            val = scalar_results[call_count]
            call_count += 1
            return val

        mock_session.scalar = AsyncMock(side_effect=mock_scalar)

        result = await service.get_course_analytics("course-1")

        assert isinstance(result, CourseProgressAnalytics)
        assert result.total_students == 5
        assert result.active_students == 3
        assert result.average_completion_rate == 0.65
        assert result.average_mastery_score == 0.72
        assert result.total_assessments_taken == 10
        assert result.average_assessment_score == 0.78

    @pytest.mark.asyncio
    async def test_get_course_analytics_empty(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        mock_session.scalar = AsyncMock(return_value=0)

        result = await service.get_course_analytics("course-empty")

        assert result.total_students == 0
        assert result.active_students == 0
        assert result.average_completion_rate == 0.0
        assert result.average_mastery_score == 0.0
        assert result.total_assessments_taken == 0
        assert result.average_assessment_score == 0.0

    @pytest.mark.asyncio
    async def test_get_system_overview(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        user_count_result = MagicMock()
        user_count_result.all.return_value = [
            (UserRole.STUDENT, 50),
            (UserRole.TEACHER, 10),
            (UserRole.ADMIN, 2),
            (UserRole.PARENT, 20),
        ]
        mock_session.execute = AsyncMock(return_value=user_count_result)

        scalar_values = [8, 80, 200, 15]
        call_count = 0

        async def mock_scalar(stmt):
            nonlocal call_count
            val = scalar_values[call_count]
            call_count += 1
            return val

        mock_session.scalar = AsyncMock(side_effect=mock_scalar)

        result = await service.get_system_overview()

        assert isinstance(result, SystemOverview)
        assert result.total_users == 82
        assert result.total_students == 50
        assert result.total_teachers == 10
        assert result.total_courses == 8
        assert result.total_enrollments == 80
        assert result.total_assessment_attempts == 200
        assert result.active_sessions_today == 15

    @pytest.mark.asyncio
    async def test_get_system_overview_no_users(self, mock_session) -> None:
        service = AnalyticsService(mock_session)

        user_count_result = MagicMock()
        user_count_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=user_count_result)

        mock_session.scalar = AsyncMock(return_value=0)

        result = await service.get_system_overview()

        assert result.total_users == 0
        assert result.total_students == 0
        assert result.total_teachers == 0
        assert result.total_courses == 0
