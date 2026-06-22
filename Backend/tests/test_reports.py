from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from app.common.types import ReportType, UserRole
from app.reports.models import Report
from app.reports.prompts import REPORT_GENERATION_PROMPT, SYSTEM_REPORT_GENERATION
from app.reports.schemas import (
    ChallengeItem,
    RecommendationItem,
    ReportData,
    ReportListItem,
    ReportResponse,
    RiskIndicator,
    StrengthItem,
)
from app.reports.service import ReportService, _report_list_item
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


def _make_report(
    report_id: str = "rpt-1",
    student_id: str = "sp-1",
    parent_id: str = "parent-1",
    report_type: str = "weekly",
) -> Mock:
    report = Mock(spec=Report)
    report.id = report_id
    report.student_id = student_id
    report.parent_id = parent_id
    report.report_type = ReportType(report_type)
    report.title = "Weekly Learning Progress Report"
    report.generated_at = datetime(2026, 6, 22, tzinfo=timezone.utc)
    report.summary = "Test summary"
    report.recommendations = []
    report.report_data = {
        "title": "Weekly Learning Progress Report",
        "executive_summary": "Test summary",
        "strengths": [
            {
                "description": "Strong in fractions",
                "category": "academic",
                "evidence": ["85% mastery on fraction concepts"],
            }
        ],
        "challenges": [
            {
                "description": "Struggles with algebra",
                "category": "conceptual",
                "severity": "high",
                "concept_title": "Algebra Basics",
            }
        ],
        "recommendations": [
            {
                "description": "Practice algebra daily",
                "priority": "high",
                "category": "practice",
            }
        ],
        "risk_indicators": [
            {
                "risk_type": "pacing",
                "description": "Falling behind in Math",
                "severity": "high",
                "actionable": True,
            }
        ],
    }
    report.is_read = False
    report.created_at = datetime(2026, 6, 22, tzinfo=timezone.utc)
    return report


# ---------------------------------------------------------------------------
# Schema Tests
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_strength_item(self) -> None:
        s = StrengthItem(
            description="Strong in fractions",
            category="academic",
            evidence=["85% mastery"],
        )
        assert s.description == "Strong in fractions"
        assert s.category == "academic"
        assert len(s.evidence) == 1

    def test_challenge_item(self) -> None:
        c = ChallengeItem(
            description="Struggles with algebra",
            category="conceptual",
            severity="high",
            concept_title="Algebra Basics",
        )
        assert c.severity == "high"
        assert c.concept_title == "Algebra Basics"

    def test_recommendation_item(self) -> None:
        r = RecommendationItem(
            description="Practice algebra daily",
            priority="high",
            category="practice",
        )
        assert r.priority == "high"

    def test_risk_indicator(self) -> None:
        ri = RiskIndicator(
            risk_type="pacing",
            description="Falling behind",
            severity="high",
            actionable=True,
        )
        assert ri.risk_type == "pacing"
        assert ri.actionable is True

    def test_report_data(self) -> None:
        rd = ReportData(
            title="Weekly Report",
            executive_summary="Good progress",
            strengths=[
                StrengthItem(description="Strong in math"),
            ],
            challenges=[
                ChallengeItem(description="Needs reading practice"),
            ],
            recommendations=[
                RecommendationItem(description="Read daily"),
            ],
            risk_indicators=[
                RiskIndicator(risk_type="engagement", description="Low engagement"),
            ],
        )
        assert rd.title == "Weekly Report"
        assert len(rd.strengths) == 1
        assert len(rd.challenges) == 1
        assert len(rd.recommendations) == 1
        assert len(rd.risk_indicators) == 1

    def test_report_response(self) -> None:
        r = ReportResponse(
            id="rpt-1",
            student_id="sp-1",
            parent_id="parent-1",
            report_type="weekly",
            title="Weekly Report",
            generated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
            summary="Good progress",
            recommendations=[],
            report_data=None,
            is_read=False,
        )
        assert r.id == "rpt-1"
        assert r.report_type == "weekly"

    def test_report_list_item(self) -> None:
        item = ReportListItem(
            id="rpt-1",
            student_id="sp-1",
            report_type="weekly",
            title="Weekly Report",
            generated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
            summary="Good progress",
            is_read=False,
        )
        assert item.id == "rpt-1"
        assert item.title == "Weekly Report"


# ---------------------------------------------------------------------------
# Service Tests
# ---------------------------------------------------------------------------


class TestReportService:
    @pytest.mark.asyncio
    async def test_generate_report_success(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = _make_user()
        profile = _make_student_profile()
        student_user = _make_user(
            user_id="student-user-1", role=UserRole.STUDENT, full_name="Child Name"
        )

        link = Mock(spec=ParentStudentLink)
        link.student = profile

        service._verify_parent_access = AsyncMock(return_value=profile)
        service.user_repo.get = AsyncMock(return_value=student_user)
        service._collect_student_data = AsyncMock(
            return_value={
                "profile": {"grade_level": "Grade 5", "current_streak_days": 3, "avg_session_duration_minutes": 25},
                "progress": {"total_lessons": 10, "completed_lessons": 5, "in_progress_lessons": 2},
                "mastery": {"total_concepts": 5, "mastered_concepts": 2, "average_mastery": 0.6, "concepts": []},
                "misconceptions": [],
                "knowledge_gaps": [],
                "pacing": [],
                "sessions": {"total": 3, "recent": []},
                "attempts": {"total": 5, "recent_correct": 3, "recent_total": 5},
            }
        )
        service._build_prompt_context = Mock(return_value="formatted context")
        service._generate_with_ai = AsyncMock(
            return_value={
                "title": "Weekly Learning Update",
                "executive_summary": "Great progress this week",
                "strengths": [
                    {
                        "description": "Strong in fractions",
                        "category": "academic",
                        "evidence": ["85% mastery"],
                    }
                ],
                "challenges": [
                    {
                        "description": "Needs algebra practice",
                        "category": "conceptual",
                        "severity": "medium",
                        "concept_title": "Algebra",
                    }
                ],
                "recommendations": [
                    {
                        "description": "Practice algebra",
                        "priority": "high",
                        "category": "practice",
                    }
                ],
                "risk_indicators": [
                    {
                        "risk_type": "pacing",
                        "description": "Behind schedule",
                        "severity": "medium",
                        "actionable": True,
                    }
                ],
            }
        )

        report_mock = Mock(spec=Report)
        report_mock.id = "rpt-1"
        report_mock.student_id = "sp-1"
        report_mock.parent_id = "parent-1"
        report_mock.report_type = ReportType.WEEKLY
        report_mock.title = "Weekly Learning Update"
        report_mock.generated_at = datetime(2026, 6, 22, tzinfo=timezone.utc)
        report_mock.summary = "Great progress this week"
        report_mock.recommendations = []
        report_mock.report_data = {
            "title": "Weekly Learning Update",
            "executive_summary": "Great progress this week",
            "strengths": [{"description": "Strong in fractions", "category": "academic", "evidence": ["85% mastery"]}],
            "challenges": [{"description": "Needs algebra practice", "category": "conceptual", "severity": "medium", "concept_title": "Algebra"}],
            "recommendations": [{"description": "Practice algebra", "priority": "high", "category": "practice"}],
            "risk_indicators": [{"risk_type": "pacing", "description": "Behind schedule", "severity": "medium", "actionable": True}],
        }
        report_mock.is_read = False
        report_mock.created_at = datetime(2026, 6, 22, tzinfo=timezone.utc)

        now = datetime(2026, 6, 22, tzinfo=timezone.utc)

        async def _mock_refresh(report):
            report.id = "rpt-1"
            report.is_read = False
            report.created_at = now

        session.refresh = AsyncMock(side_effect=_mock_refresh)

        result = await service.generate_report(parent_user, "sp-1", "weekly")

        assert result.id == "rpt-1"
        assert result.title == "Weekly Learning Update"
        assert result.report_data is not None
        assert len(result.report_data.strengths) == 1
        assert result.report_data.strengths[0].description == "Strong in fractions"
        assert len(result.report_data.risk_indicators) == 1
        assert result.report_data.risk_indicators[0].risk_type == "pacing"

    @pytest.mark.asyncio
    async def test_generate_report_fallback(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = _make_user()
        profile = _make_student_profile()
        student_user = _make_user(
            user_id="student-user-1", role=UserRole.STUDENT, full_name="Child"
        )

        service._verify_parent_access = AsyncMock(return_value=profile)
        service.user_repo.get = AsyncMock(return_value=student_user)
        service._collect_student_data = AsyncMock(return_value={})
        service._build_prompt_context = Mock(return_value="context")

        with patch.object(service.gemini, "generate_json", AsyncMock(side_effect=Exception("API error"))):
            now = datetime(2026, 6, 22, tzinfo=timezone.utc)

            async def _mock_refresh(report):
                report.id = "rpt-1"
                report.is_read = False
                report.created_at = now

            session.refresh = AsyncMock(side_effect=_mock_refresh)

            result = await service.generate_report(parent_user, "sp-1", "weekly")
            assert result.title == "Weekly Learning Progress Report"
            assert result.report_data is not None
            assert len(result.report_data.strengths) == 1

    @pytest.mark.asyncio
    async def test_generate_report_student_forbidden(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        student_user = _make_user(user_id="stu-1", role=UserRole.STUDENT)

        with pytest.raises(Exception):
            await service.generate_report(student_user, "sp-1")

    @pytest.mark.asyncio
    async def test_get_report_found(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = _make_user()

        report = _make_report()
        mock_result = Mock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = report
        session.execute = AsyncMock(return_value=mock_result)

        service._verify_parent_access = AsyncMock(return_value=_make_student_profile())

        result = await service.get_report(parent_user, "rpt-1")

        assert result.id == "rpt-1"
        assert result.title == "Weekly Learning Progress Report"
        assert result.report_data is not None
        assert result.report_data.executive_summary == "Test summary"

    @pytest.mark.asyncio
    async def test_get_report_not_found(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = _make_user()

        mock_result = Mock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(Exception):
            await service.get_report(parent_user, "nonexistent")

    @pytest.mark.asyncio
    async def test_get_student_reports(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = _make_user()
        profile = _make_student_profile()

        service._verify_parent_access = AsyncMock(return_value=profile)
        session.scalar = AsyncMock(return_value=2)

        r1 = _make_report(report_id="rpt-1")
        r2 = _make_report(report_id="rpt-2")

        mock_result = Mock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [r1, r2]
        session.execute = AsyncMock(return_value=mock_result)

        items, total = await service.get_student_reports(parent_user, "sp-1")

        assert total == 2
        assert len(items) == 2
        assert items[0].id == "rpt-1"
        assert items[1].id == "rpt-2"

    @pytest.mark.asyncio
    async def test_verify_parent_access_admin(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        admin_user = _make_user(user_id="admin-1", role=UserRole.ADMIN)

        profile = _make_student_profile()
        service.student_profile_repo.get = AsyncMock(return_value=profile)

        result = await service._verify_parent_access(admin_user, "sp-1")
        assert result.id == "sp-1"

    @pytest.mark.asyncio
    async def test_verify_parent_access_linked(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = _make_user()

        profile = _make_student_profile()
        link = Mock(spec=ParentStudentLink)
        link.student = profile

        mock_result = Mock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = link
        session.execute = AsyncMock(return_value=mock_result)

        result = await service._verify_parent_access(parent_user, "sp-1")
        assert result.id == "sp-1"

    @pytest.mark.asyncio
    async def test_verify_parent_access_not_linked(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = _make_user()

        mock_result = Mock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(Exception):
            await service._verify_parent_access(parent_user, "sp-1")

    @pytest.mark.asyncio
    async def test_verify_parent_access_student_forbidden(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        student_user = _make_user(user_id="stu-1", role=UserRole.STUDENT)

        with pytest.raises(Exception):
            await service._verify_parent_access(student_user, "sp-1")

    @pytest.mark.asyncio
    async def test_collect_student_data(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        profile = _make_student_profile()

        service.progress_repo.find_by_student = AsyncMock(return_value=[])
        service.mastery_repo.find_by_student = AsyncMock(return_value=[])

        mock_empty = Mock()
        mock_empty.unique.return_value.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=mock_empty)

        service.enrollment_repo.find_by_student = AsyncMock(return_value=[])

        data = await service._collect_student_data(profile)

        assert "profile" in data
        assert "progress" in data
        assert "mastery" in data
        assert data["profile"]["grade_level"] == "Grade 5"
        assert data["mastery"]["total_concepts"] == 0
        assert data["progress"]["total_lessons"] == 0

    @pytest.mark.asyncio
    async def test_generate_with_ai_success(self) -> None:
        session = AsyncMock()
        service = ReportService(session)

        expected = {
            "title": "Test Report",
            "executive_summary": "Good progress",
            "strengths": [{"description": "Math strength", "category": "academic", "evidence": []}],
            "challenges": [{"description": "Reading challenge", "category": "conceptual", "severity": "medium", "concept_title": None}],
            "recommendations": [{"description": "Read more", "priority": "medium", "category": "practice"}],
            "risk_indicators": [],
        }

        with patch.object(service.gemini, "generate_json", AsyncMock(return_value=expected)):
            result = await service._generate_with_ai("test context")

        assert result["title"] == "Test Report"
        assert result["executive_summary"] == "Good progress"
        assert len(result["strengths"]) == 1

    @pytest.mark.asyncio
    async def test_generate_with_ai_fallback(self) -> None:
        session = AsyncMock()
        service = ReportService(session)

        with patch.object(service.gemini, "generate_json", AsyncMock(side_effect=Exception("API error"))):
            result = await service._generate_with_ai("test context")

        assert result["title"] == "Weekly Learning Progress Report"
        assert len(result["strengths"]) == 1
        assert len(result["risk_indicators"]) == 0

    def test_validate_report_data_full(self) -> None:
        session = AsyncMock()
        service = ReportService(session)

        raw = {
            "title": "Validated Report",
            "executive_summary": "Doing well",
            "strengths": [
                {"description": "Strength 1", "category": "academic", "evidence": ["data"]},
            ],
            "challenges": [
                {"description": "Challenge 1", "category": "conceptual", "severity": "high", "concept_title": "Concept A"},
            ],
            "recommendations": [
                {"description": "Recommendation 1", "priority": "high", "category": "practice"},
            ],
            "risk_indicators": [
                {"risk_type": "pacing", "description": "Risk 1", "severity": "medium", "actionable": True},
            ],
        }

        result = service._validate_report_data(raw)
        assert result["title"] == "Validated Report"
        assert len(result["strengths"]) == 1
        assert len(result["challenges"]) == 1
        assert len(result["recommendations"]) == 1
        assert len(result["risk_indicators"]) == 1

    def test_validate_report_data_filters_bad_items(self) -> None:
        session = AsyncMock()
        service = ReportService(session)

        raw = {
            "title": "Test",
            "executive_summary": "Summary",
            "strengths": [
                {"description": "Valid strength", "category": "academic", "evidence": []},
                {"bad": "data"},
                {},
            ],
            "challenges": [
                {"description": "Valid challenge", "category": "conceptual", "severity": "low"},
                {"no_description": True},
            ],
            "recommendations": [
                {"no_description": True},
            ],
            "risk_indicators": [
                {"risk_type": "pace", "description": "Risk"},
                {"risk_type": "bad"},
                {},
            ],
        }

        result = service._validate_report_data(raw)
        assert len(result["strengths"]) == 1
        assert len(result["challenges"]) == 1
        assert len(result["recommendations"]) == 0
        assert len(result["risk_indicators"]) == 1

    def test_fallback_report_data(self) -> None:
        session = AsyncMock()
        service = ReportService(session)

        result = service._fallback_report_data("some context")
        assert result["title"] == "Weekly Learning Progress Report"
        assert len(result["strengths"]) == 1
        assert len(result["challenges"]) == 1
        assert len(result["recommendations"]) == 1
        assert len(result["risk_indicators"]) == 0

    def test_report_list_item(self) -> None:
        report = _make_report()
        item = _report_list_item(report)
        assert item.id == "rpt-1"
        assert item.student_id == "sp-1"
        assert item.report_type == "weekly"
        assert isinstance(item, ReportListItem)


# ---------------------------------------------------------------------------
# Router Tests
# ---------------------------------------------------------------------------


class TestRouter:
    def test_router_prefix(self) -> None:
        from app.reports.router import router

        assert router.prefix == "/api/v1/reports"

    def test_router_tags(self) -> None:
        from app.reports.router import router

        assert "Reports" in router.tags

    def test_routes_registered(self) -> None:
        from app.reports.router import router

        paths = [r.path for r in router.routes]
        assert "/api/v1/reports/generate/{student_id}" in paths
        assert "/api/v1/reports/{report_id}" in paths
        assert "/api/v1/reports/student/{student_id}" in paths

    @pytest.mark.asyncio
    async def test_generate_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient

        from app.auth.dependencies import get_current_active_user
        from app.infrastructure.database import get_session
        from app.main import app
        from app.reports.schemas import ReportResponse

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
            "app.reports.service.ReportService.generate_report",
            new_callable=AsyncMock,
        ) as mock_gen:
            mock_gen.return_value = ReportResponse(
                id="rpt-1",
                student_id="sp-1",
                parent_id="parent-1",
                report_type="weekly",
                title="Weekly Learning Update",
                generated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
                summary="Great progress this week",
                recommendations=[],
                report_data=None,
                is_read=False,
                created_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/reports/generate/sp-1?report_type=weekly"
                )

                assert response.status_code == 200, response.text
                data = response.json()
                assert data["status"] == "success"
                report = data["data"]
                assert report["id"] == "rpt-1"
                assert report["title"] == "Weekly Learning Update"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_report_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient

        from app.auth.dependencies import get_current_active_user
        from app.infrastructure.database import get_session
        from app.main import app
        from app.reports.schemas import ReportResponse

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
            "app.reports.service.ReportService.get_report",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = ReportResponse(
                id="rpt-1",
                student_id="sp-1",
                parent_id="parent-1",
                report_type="weekly",
                title="Weekly Report",
                generated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
                summary="Summary text",
                recommendations=[],
                report_data=None,
                is_read=False,
                created_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/reports/rpt-1")

                assert response.status_code == 200, response.text
                data = response.json()
                assert data["status"] == "success"
                assert data["data"]["id"] == "rpt-1"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_list_student_reports_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient

        from app.auth.dependencies import get_current_active_user
        from app.infrastructure.database import get_session
        from app.main import app
        from app.reports.schemas import ReportListItem

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
            "app.reports.service.ReportService.get_student_reports",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = (
                [
                    ReportListItem(
                        id="rpt-1",
                        student_id="sp-1",
                        report_type="weekly",
                        title="Weekly Report 1",
                        generated_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
                        summary="Summary 1",
                        is_read=False,
                        created_at=datetime(2026, 6, 22, tzinfo=timezone.utc),
                    ),
                ],
                1,
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/reports/student/sp-1")

                assert response.status_code == 200, response.text
                data = response.json()
                assert data["status"] == "success"
                assert len(data["data"]) == 1
                assert data["data"][0]["id"] == "rpt-1"
                assert data["meta"]["total"] == 1

        app.dependency_overrides.clear()
