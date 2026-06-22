from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from app.common.types import (
    EnrollmentStatus,
    LessonProgressStatus,
    MisconceptionCategory,
    PaceStatus,
    SessionState,
    UserRole,
)
from app.diagnosis.models import Misconception
from app.enrollment.models import CourseSchedule, StudentCourseEnrollment
from app.parent_dashboard.repository import (
    MisconceptionRepository,
    ParentStudentLinkRepository,
    ParentTeachingSessionRepository,
)
from app.parent_dashboard.schemas import (
    CurriculumNode,
    CurriculumTreeResponse,
    DashboardResponse,
    KnowledgeGapResponse,
    MasteryConceptResponse,
    MasterySummaryResponse,
    MisconceptionResponse,
    PacingStatusResponse,
    ParentStudentResponse,
    ProgressSummaryResponse,
    RecentActivityItem,
    StudentProfileResponse,
    TeachingSessionResponse,
)
from app.parent_dashboard.service import ParentDashboardService
from app.teaching.models import TeachingSession
from app.users.models import ParentStudentLink, StudentProfile, User


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_user(
    user_id: str = "user-1",
    role: UserRole = UserRole.PARENT,
    full_name: str = "Test Parent",
) -> User:
    user = Mock(spec=User)
    user.id = user_id
    user.role = role
    user.full_name = full_name
    user.email = "parent@test.com"
    user.is_active = True
    return user


def _make_student_profile(
    profile_id: str = "sp-1",
    user_id: str = "student-user-1",
    grade_level: str = "Grade 5",
    streak: int = 3,
) -> StudentProfile:
    profile = Mock(spec=StudentProfile)
    profile.id = profile_id
    profile.user_id = user_id
    profile.grade_level = grade_level
    profile.current_streak_days = streak
    profile.avg_session_duration_minutes = 25
    profile.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return profile


# ---------------------------------------------------------------------------
# Repository Tests
# ---------------------------------------------------------------------------


class TestParentStudentLinkRepository:
    @pytest.mark.asyncio
    async def test_find_by_parent(self) -> None:
        session = AsyncMock()
        repo = ParentStudentLinkRepository(session)

        mock_result = Mock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=mock_result)

        await repo.find_by_parent("parent-1")

        stmt = session.execute.call_args[0][0]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "parent_student_links" in compiled
        assert "parent-1" in compiled

    @pytest.mark.asyncio
    async def test_find_by_parent_and_student(self) -> None:
        session = AsyncMock()
        repo = ParentStudentLinkRepository(session)

        mock_result = Mock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)

        await repo.find_by_parent_and_student("parent-1", "sp-1")

        stmt = session.execute.call_args[0][0]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "parent-1" in compiled
        assert "sp-1" in compiled


class TestMisconceptionRepository:
    @pytest.mark.asyncio
    async def test_find_active_by_student(self) -> None:
        session = AsyncMock()
        repo = MisconceptionRepository(session)

        mock_result = Mock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=mock_result)

        await repo.find_active_by_student("sp-1")

        stmt = session.execute.call_args[0][0]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "misconceptions" in compiled

    @pytest.mark.asyncio
    async def test_find_knowledge_gaps(self) -> None:
        session = AsyncMock()
        repo = MisconceptionRepository(session)

        mock_result = Mock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=mock_result)

        await repo.find_knowledge_gaps("sp-1")

        stmt = session.execute.call_args[0][0]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "misconceptions" in compiled
        assert "conceptual" in compiled.lower()


class TestParentTeachingSessionRepository:
    @pytest.mark.asyncio
    async def test_find_recent_by_student(self) -> None:
        session = AsyncMock()
        repo = ParentTeachingSessionRepository(session)

        mock_result = Mock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=mock_result)

        await repo.find_recent_by_student("sp-1", days=7)

        stmt = session.execute.call_args[0][0]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "teaching_sessions" in compiled

    @pytest.mark.asyncio
    async def test_count_by_student(self) -> None:
        session = AsyncMock()
        repo = ParentTeachingSessionRepository(session)
        session.scalar = AsyncMock(return_value=5)
        result = await repo.count_by_student("sp-1")
        assert result == 5


# ---------------------------------------------------------------------------
# Schema Tests
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_parent_student_response(self) -> None:
        s = ParentStudentResponse(
            student_id="sp-1",
            full_name="Child Name",
            grade_level="Grade 5",
            current_streak_days=3,
        )
        assert s.student_id == "sp-1"
        assert s.full_name == "Child Name"

    def test_student_profile_response(self) -> None:
        dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        s = StudentProfileResponse(
            student_id="sp-1",
            full_name="Child",
            email="child@test.com",
            grade_level="Grade 5",
            current_streak_days=3,
            avg_session_duration_minutes=25,
            created_at=dt,
        )
        assert s.email == "child@test.com"

    def test_progress_summary_response(self) -> None:
        s = ProgressSummaryResponse(
            total_lessons=20,
            completed_lessons=10,
            in_progress_lessons=3,
            not_started_lessons=7,
            completion_percentage=50.0,
        )
        assert s.completion_percentage == 50.0

    def test_mastery_concept_response(self) -> None:
        s = MasteryConceptResponse(
            concept_id="c-1",
            concept_title="Variables",
            lesson_title="Intro to Programming",
            mastery_level=0.85,
            total_attempts=10,
            consecutive_correct=5,
        )
        assert s.mastery_level == 0.85

    def test_mastery_summary_response(self) -> None:
        s = MasterySummaryResponse(
            total_concepts=10,
            mastered_concepts=5,
            in_progress_concepts=3,
            not_started_concepts=2,
            average_mastery=0.6,
            concepts=[],
        )
        assert s.mastered_concepts == 5

    def test_pacing_status_response(self) -> None:
        s = PacingStatusResponse(
            enrollment_id="e-1",
            course_id="c-1",
            course_title="Math",
            current_week=3,
            target_lessons_per_week=4,
            pace_status="on_track",
        )
        assert s.pace_status == "on_track"

    def test_misconception_response(self) -> None:
        dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        s = MisconceptionResponse(
            misconception_id="m-1",
            concept_id="c-1",
            concept_title="Variables",
            category="conceptual",
            description="Thinks variables are constant",
            detected_at=dt,
            frequency=3,
            is_resolved=False,
        )
        assert s.frequency == 3
        assert s.is_resolved is False

    def test_knowledge_gap_response(self) -> None:
        s = KnowledgeGapResponse(
            gap_id="m-1",
            concept_id="c-1",
            concept_title="Functions",
            description="Missing function understanding",
            detected_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            frequency=2,
        )
        assert s.description == "Missing function understanding"

    def test_teaching_session_response(self) -> None:
        s = TeachingSessionResponse(
            session_id="ses-1",
            course_id="c-1",
            course_title="Math",
            concept_title="Variables",
            state="active",
            started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert s.state == "active"

    def test_recent_activity_item(self) -> None:
        s = RecentActivityItem(
            activity_type="session",
            description="Teaching session",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            session_id="ses-1",
            concept_title="Variables",
        )
        assert s.activity_type == "session"

    def test_dashboard_response(self) -> None:
        dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        dashboard = DashboardResponse(
            student=StudentProfileResponse(
                student_id="sp-1", full_name="Child", email="c@t.com"
            ),
            progress=ProgressSummaryResponse(),
            mastery=MasterySummaryResponse(),
            active_misconceptions=[
                MisconceptionResponse(
                    misconception_id="m-1",
                    concept_id="c-1",
                    description="Test",
                )
            ],
            knowledge_gaps=[],
            pacing=[],
            recent_sessions=[],
            recent_activity=[],
            learning_streak_days=3,
            completion_forecast={},
        )
        assert dashboard.learning_streak_days == 3
        assert len(dashboard.active_misconceptions) == 1

    def test_curriculum_node(self) -> None:
        node = CurriculumNode(
            module_id="mod-1",
            module_title="Module 1",
            module_order=1,
            lessons=[{"lesson_id": "l-1", "lesson_title": "Lesson 1"}],
        )
        assert node.module_title == "Module 1"
        assert len(node.lessons) == 1

    def test_curriculum_tree_response(self) -> None:
        tree = CurriculumTreeResponse(
            course_id="c-1",
            course_title="Math",
            modules=[
                CurriculumNode(
                    module_id="mod-1",
                    module_title="M1",
                    module_order=1,
                    lessons=[],
                )
            ],
        )
        assert tree.course_title == "Math"


# ---------------------------------------------------------------------------
# Service Tests
# ---------------------------------------------------------------------------


class TestParentDashboardService:
    @pytest.mark.asyncio
    async def test_get_linked_students_parent(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()

        student_profile = _make_student_profile()
        student_user = _make_user(
            user_id="student-user-1",
            role=UserRole.STUDENT,
            full_name="Child Name",
        )

        link = Mock(spec=ParentStudentLink)
        link.student_id = "sp-1"
        link.student = student_profile

        service.parent_link_repo.find_by_parent = AsyncMock(return_value=[link])
        service.user_repo.get = AsyncMock(return_value=student_user)

        result = await service.get_linked_students(parent_user)

        assert len(result) == 1
        assert result[0].student_id == "sp-1"
        assert result[0].full_name == "Child Name"
        assert result[0].current_streak_days == 3

    @pytest.mark.asyncio
    async def test_get_linked_students_admin(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        admin_user = _make_user(user_id="admin-1", role=UserRole.ADMIN)

        student_profile = _make_student_profile()
        student_user = _make_user(
            user_id="student-user-1",
            role=UserRole.STUDENT,
            full_name="Student",
        )

        service.student_profile_repo.find = AsyncMock(return_value=[student_profile])
        service.user_repo.get = AsyncMock(return_value=student_user)

        result = await service.get_linked_students(admin_user)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_linked_students_student_forbidden(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        student_user = _make_user(user_id="stu-1", role=UserRole.STUDENT)

        with pytest.raises(Exception):
            await service.get_linked_students(student_user)

    @pytest.mark.asyncio
    async def test_verify_parent_access_admin(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        admin_user = _make_user(user_id="admin-1", role=UserRole.ADMIN)

        profile = _make_student_profile()
        service.student_profile_repo.get = AsyncMock(return_value=profile)

        result = await service._verify_parent_access(admin_user, "sp-1")
        assert result.id == "sp-1"

    @pytest.mark.asyncio
    async def test_verify_parent_access_linked(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()

        profile = _make_student_profile()
        link = Mock(spec=ParentStudentLink)
        link.student = profile

        service.parent_link_repo.find_by_parent_and_student = AsyncMock(
            return_value=link
        )

        result = await service._verify_parent_access(parent_user, "sp-1")
        assert result.id == "sp-1"

    @pytest.mark.asyncio
    async def test_verify_parent_access_not_linked(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()

        service.parent_link_repo.find_by_parent_and_student = AsyncMock(
            return_value=None
        )

        with pytest.raises(Exception):
            await service._verify_parent_access(parent_user, "sp-1")

    @pytest.mark.asyncio
    async def test_verify_parent_access_student_forbidden(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        student_user = _make_user(user_id="stu-1", role=UserRole.STUDENT)

        with pytest.raises(Exception):
            await service._verify_parent_access(student_user, "sp-1")

    @pytest.mark.asyncio
    async def test_get_student_profile(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()

        profile = _make_student_profile()
        user = _make_user(user_id="student-user-1", full_name="Child Name")

        service._verify_parent_access = AsyncMock(return_value=profile)
        service.user_repo.get = AsyncMock(return_value=user)

        result = await service.get_student_profile(parent_user, "sp-1")

        assert result.full_name == "Child Name"
        assert result.email == "parent@test.com"
        assert result.grade_level == "Grade 5"

    @pytest.mark.asyncio
    async def test_get_progress_summary(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()
        profile = _make_student_profile()

        service._verify_parent_access = AsyncMock(return_value=profile)

        p1 = Mock(spec=LessonProgressStatus)
        p1.status = LessonProgressStatus.COMPLETED
        p2 = Mock(spec=LessonProgressStatus)
        p2.status = LessonProgressStatus.IN_PROGRESS
        p3 = Mock(spec=LessonProgressStatus)
        p3.status = LessonProgressStatus.NOT_STARTED

        progress_mocks = [Mock(), Mock(), Mock()]
        progress_mocks[0].status = LessonProgressStatus.COMPLETED
        progress_mocks[1].status = LessonProgressStatus.IN_PROGRESS
        progress_mocks[2].status = LessonProgressStatus.NOT_STARTED

        service.progress_repo.find_by_student = AsyncMock(return_value=progress_mocks)

        result = await service.get_progress_summary(parent_user, "sp-1")

        assert result.total_lessons == 3
        assert result.completed_lessons == 1
        assert result.in_progress_lessons == 1
        assert result.not_started_lessons == 1
        assert result.completion_percentage == pytest.approx(33.3, rel=1e-1)

    @pytest.mark.asyncio
    async def test_get_mastery_summary(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()
        profile = _make_student_profile()

        service._verify_parent_access = AsyncMock(return_value=profile)

        r1 = Mock()
        r1.concept_id = "c-1"
        r1.mastery_level = 0.9
        r1.total_attempts = 10
        r1.consecutive_correct = 8
        r1.last_attempted_at = None
        r1.concept = Mock()
        r1.concept.title = "Variables"
        r1.concept.lesson = Mock()
        r1.concept.lesson.title = "Intro"

        r2 = Mock()
        r2.concept_id = "c-2"
        r2.mastery_level = 0.4
        r2.total_attempts = 3
        r2.consecutive_correct = 1
        r2.last_attempted_at = None
        r2.concept = Mock()
        r2.concept.title = "Functions"
        r2.concept.lesson = Mock()
        r2.concept.lesson.title = "Advanced"

        service.mastery_repo.find_by_student = AsyncMock(return_value=[r1, r2])

        result = await service.get_mastery_summary(parent_user, "sp-1")

        assert result.total_concepts == 2
        assert result.mastered_concepts == 1
        assert result.in_progress_concepts == 1
        assert result.average_mastery == 0.65

    @pytest.mark.asyncio
    async def test_get_misconceptions(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()
        profile = _make_student_profile()

        service._verify_parent_access = AsyncMock(return_value=profile)

        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        m1 = Mock(spec=Misconception)
        m1.id = "m-1"
        m1.concept_id = "c-1"
        m1.category = "conceptual"
        m1.description = "Thinks variables are constant"
        m1.detected_at = now
        m1.frequency = 3
        m1.is_resolved = False
        m1.resolved_at = None
        m1.concept = Mock()
        m1.concept.title = "Variables"

        service.misconception_repo.find_active_by_student = AsyncMock(
            return_value=[m1]
        )

        result = await service.get_misconceptions(parent_user, "sp-1")

        assert len(result) == 1
        assert result[0].description == "Thinks variables are constant"
        assert result[0].frequency == 3

    @pytest.mark.asyncio
    async def test_get_knowledge_gaps(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()
        profile = _make_student_profile()

        service._verify_parent_access = AsyncMock(return_value=profile)

        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        m1 = Mock(spec=Misconception)
        m1.id = "m-1"
        m1.concept_id = "c-1"
        m1.description = "Missing prerequisite knowledge"
        m1.detected_at = now
        m1.frequency = 2
        m1.concept = Mock()
        m1.concept.title = "Functions"

        service.misconception_repo.find_knowledge_gaps = AsyncMock(
            return_value=[m1]
        )

        result = await service.get_knowledge_gaps(parent_user, "sp-1")

        assert len(result) == 1
        assert result[0].description == "Missing prerequisite knowledge"

    @pytest.mark.asyncio
    async def test_get_pacing(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()
        profile = _make_student_profile()

        service._verify_parent_access = AsyncMock(return_value=profile)

        enrollment = Mock(spec=StudentCourseEnrollment)
        enrollment.id = "e-1"
        enrollment.course_id = "c-1"

        schedule = Mock(spec=CourseSchedule)
        schedule.current_week = 3
        schedule.target_lessons_per_week = 4
        schedule.pace_status = PaceStatus.ON_TRACK
        schedule.last_pacing_adjustment_at = None

        service.enrollment_repo.find_by_student = AsyncMock(return_value=[enrollment])
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=schedule)

        course = Mock()
        course.title = "Math 101"
        mock_result = Mock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = course
        session.execute = AsyncMock(return_value=mock_result)

        result = await service.get_pacing(parent_user, "sp-1")

        assert len(result) == 1
        assert result[0].course_title == "Math 101"
        assert result[0].pace_status == "on_track"

    @pytest.mark.asyncio
    async def test_get_sessions(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()
        profile = _make_student_profile()

        service._verify_parent_access = AsyncMock(return_value=profile)

        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        ts = Mock(spec=TeachingSession)
        ts.id = "ses-1"
        ts.course_id = "c-1"
        ts.current_concept_id = "con-1"
        ts.state = SessionState.ACTIVE
        ts.started_at = now
        ts.last_activity_at = now
        ts.completed_at = None

        service.session_repo.find_by_student = AsyncMock(
            return_value=([ts], 1)
        )

        course = Mock()
        course.title = "Math"
        concept = Mock()
        concept.title = "Variables"

        def mock_result_factory(table: str):
            result = Mock()
            if table == "courses":
                result.unique.return_value.scalar_one_or_none.return_value = course
            elif table == "concepts":
                result.unique.return_value.scalar_one_or_none.return_value = concept
            else:
                result.unique.return_value.scalar_one_or_none.return_value = None
            return result

        calls = iter([
            mock_result_factory("courses"),
            mock_result_factory("concepts"),
        ])
        session.execute = AsyncMock(side_effect=lambda _: next(calls))

        result, total = await service.get_sessions(parent_user, "sp-1")

        assert total == 1
        assert len(result) == 1
        assert result[0].course_title == "Math"
        assert result[0].concept_title == "Variables"

    @pytest.mark.asyncio
    async def test_get_dashboard(self) -> None:
        session = AsyncMock()
        service = ParentDashboardService(session)
        parent_user = _make_user()
        profile = _make_student_profile()
        user = _make_user(user_id="student-user-1", full_name="Child Name")

        service._verify_parent_access = AsyncMock(return_value=profile)
        service.user_repo.get = AsyncMock(return_value=user)

        service.get_progress_summary = AsyncMock(return_value=ProgressSummaryResponse())
        service.get_mastery_summary = AsyncMock(return_value=MasterySummaryResponse())
        service.get_misconceptions = AsyncMock(return_value=[])
        service.get_knowledge_gaps = AsyncMock(return_value=[])
        service.get_pacing = AsyncMock(return_value=[])
        service.get_sessions = AsyncMock(return_value=([], 0))
        service.get_recent_activity = AsyncMock(return_value=[])
        service._compute_completion_forecast = AsyncMock(return_value={})

        dashboard = await service.get_dashboard(parent_user, "sp-1")

        assert isinstance(dashboard, DashboardResponse)
        assert dashboard.student.full_name == "Child Name"
        assert dashboard.learning_streak_days == 3


# ---------------------------------------------------------------------------
# Router Tests
# ---------------------------------------------------------------------------


class TestRouter:
    def test_router_prefix(self) -> None:
        from app.parent_dashboard.router import router

        assert router.prefix == "/api/v1/parents"

    def test_router_tags(self) -> None:
        from app.parent_dashboard.router import router

        assert "Parent Dashboard" in router.tags

    def test_routes_registered(self) -> None:
        from app.parent_dashboard.router import router

        paths = [r.path for r in router.routes]
        assert "/api/v1/parents/students" in paths
        assert "/api/v1/parents/students/{student_id}" in paths
        assert "/api/v1/parents/students/{student_id}/progress" in paths
        assert "/api/v1/parents/students/{student_id}/curriculum" in paths
        assert "/api/v1/parents/students/{student_id}/mastery" in paths
        assert "/api/v1/parents/students/{student_id}/mastery/concepts" in paths
        assert "/api/v1/parents/students/{student_id}/pacing" in paths
        assert "/api/v1/parents/students/{student_id}/misconceptions" in paths
        assert "/api/v1/parents/students/{student_id}/knowledge-gaps" in paths
        assert "/api/v1/parents/students/{student_id}/sessions" in paths
        assert "/api/v1/parents/students/{student_id}/recent-activity" in paths
        assert "/api/v1/parents/students/{student_id}/dashboard" in paths

    @pytest.mark.asyncio
    async def test_students_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient

        from app.auth.dependencies import get_current_active_user
        from app.infrastructure.database import get_session
        from app.main import app
        from app.parent_dashboard.router import router

        async def _override_session():
            return AsyncMock()

        async def _override_user():
            user = Mock(spec=User)
            user.id = "parent-1"
            user.role = UserRole.PARENT
            return user

        app.dependency_overrides[get_session] = _override_session
        app.dependency_overrides[get_current_active_user] = _override_user

        with patch(
            "app.parent_dashboard.service.ParentDashboardService.get_linked_students",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [
                ParentStudentResponse(
                    student_id="sp-1",
                    full_name="Child Name",
                    grade_level="Grade 5",
                    current_streak_days=3,
                )
            ]

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/parents/students")

                assert response.status_code == 200, response.text
                data = response.json()
                assert data["status"] == "success"
                students = data["data"]
                assert len(students) == 1
                assert students[0]["full_name"] == "Child Name"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_dashboard_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient

        from app.auth.dependencies import get_current_active_user
        from app.infrastructure.database import get_session
        from app.main import app

        async def _override_session():
            return AsyncMock()

        async def _override_user():
            user = Mock(spec=User)
            user.id = "parent-1"
            user.role = UserRole.PARENT
            return user

        app.dependency_overrides[get_session] = _override_session
        app.dependency_overrides[get_current_active_user] = _override_user

        with patch(
            "app.parent_dashboard.service.ParentDashboardService.get_dashboard",
            new_callable=AsyncMock,
        ) as mock_dash:
            mock_dash.return_value = DashboardResponse(
                student=StudentProfileResponse(
                    student_id="sp-1",
                    full_name="Child Name",
                    email="child@test.com",
                ),
                progress=ProgressSummaryResponse(
                    total_lessons=10,
                    completed_lessons=5,
                    completion_percentage=50.0,
                ),
                mastery=MasterySummaryResponse(),
                active_misconceptions=[],
                knowledge_gaps=[],
                pacing=[],
                recent_sessions=[],
                recent_activity=[],
                learning_streak_days=3,
                completion_forecast={},
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/parents/students/sp-1/dashboard"
                )

                assert response.status_code == 200, response.text
                data = response.json()
                assert data["status"] == "success"
                dash = data["data"]
                assert dash["student"]["full_name"] == "Child Name"
                assert dash["progress"]["completed_lessons"] == 5
                assert dash["learning_streak_days"] == 3

        app.dependency_overrides.clear()
