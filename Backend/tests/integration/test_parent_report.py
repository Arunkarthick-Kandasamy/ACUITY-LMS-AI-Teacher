from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.common.types import ReportType, UserRole
from app.reports.prompts import REPORT_GENERATION_PROMPT, SYSTEM_REPORT_GENERATION
from app.reports.schemas import ReportResponse
from app.reports.service import ReportService
from app.users.models import StudentProfile, User


class TestParentReportFlow:
    @pytest.mark.asyncio
    async def test_report_generation_flow(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = Mock(spec=User)
        parent_user.id = "parent-1"
        parent_user.role = UserRole.PARENT

        profile = Mock(spec=StudentProfile)
        profile.id = "sp-1"
        profile.user_id = "student-user-1"
        profile.grade_level = "Grade 5"
        profile.current_streak_days = 5
        profile.avg_session_duration_minutes = 30

        student_user = Mock(spec=User)
        student_user.full_name = "Child Name"

        service._verify_parent_access = AsyncMock(return_value=profile)
        service.user_repo.get = AsyncMock(return_value=student_user)
        service._collect_student_data = AsyncMock(
            return_value={
                "profile": {"grade_level": "Grade 5", "current_streak_days": 5, "avg_session_duration_minutes": 30},
                "progress": {"total_lessons": 20, "completed_lessons": 12, "in_progress_lessons": 3},
                "mastery": {
                    "total_concepts": 10,
                    "mastered_concepts": 6,
                    "average_mastery": 0.72,
                    "concepts": [
                        {"concept_id": "c1", "title": "Fractions", "mastery_level": 0.85, "total_attempts": 8},
                        {"concept_id": "c2", "title": "Decimals", "mastery_level": 0.45, "total_attempts": 5},
                    ],
                },
                "misconceptions": [
                    {"concept_title": "Decimals", "category": "conceptual", "description": "Confuses tenths and hundredths", "frequency": 3},
                ],
                "knowledge_gaps": [],
                "pacing": [{"course_title": "Math 101", "current_week": 4, "target_lessons_per_week": 3, "pace_status": "on_track"}],
                "sessions": {"total": 8, "recent": [{"state": "active", "last_activity_at": "2026-06-22T10:00:00"}]},
                "attempts": {"total": 15, "recent_correct": 10, "recent_total": 15},
            }
        )

        expected_report_data = {
            "title": "Weekly Learning Update - Great Progress in Math!",
            "executive_summary": "Child Name has made solid progress this week, mastering 6 out of 10 concepts.",
            "strengths": [
                {"description": "Strong understanding of fractions", "category": "academic", "evidence": ["85% mastery on fraction concepts"]},
            ],
            "challenges": [
                {"description": "Struggling with decimal place values", "category": "conceptual", "severity": "medium", "concept_title": "Decimals"},
            ],
            "recommendations": [
                {"description": "Practice decimal conversions at home", "priority": "high", "category": "practice"},
            ],
            "risk_indicators": [],
        }

        def _mock_generate(prompt: str, system_instruction: str | None = None) -> dict:
            return expected_report_data

        with patch.object(service.gemini, "generate_json", AsyncMock(side_effect=_mock_generate)):
            async def _mock_refresh(report):
                report.id = "rpt-1"
                report.is_read = False
                report.created_at = None

            session.refresh = AsyncMock(side_effect=_mock_refresh)

            result = await service.generate_report(parent_user, "sp-1", "weekly")

        assert result.title == "Weekly Learning Update - Great Progress in Math!"
        assert result.report_data is not None
        assert len(result.report_data.strengths) == 1
        assert len(result.report_data.challenges) == 1
        assert len(result.report_data.recommendations) == 1

    @pytest.mark.asyncio
    async def test_report_context_builds_from_data(self) -> None:
        session = AsyncMock()
        service = ReportService(session)

        student_user = Mock(spec=User)
        student_user.full_name = "Test Student"

        data = {
            "profile": {"grade_level": "Grade 5", "current_streak_days": 3, "avg_session_duration_minutes": 25},
            "progress": {"total_lessons": 10, "completed_lessons": 5, "in_progress_lessons": 2},
            "mastery": {
                "total_concepts": 4,
                "mastered_concepts": 2,
                "average_mastery": 0.6,
                "concepts": [
                    {"concept_id": "c1", "title": "Fractions", "mastery_level": 0.9, "total_attempts": 10},
                    {"concept_id": "c2", "title": "Decimals", "mastery_level": 0.3, "total_attempts": 4},
                ],
            },
            "misconceptions": [],
            "knowledge_gaps": [],
            "pacing": [],
            "sessions": {"total": 3, "recent": []},
            "attempts": {"total": 5, "recent_correct": 3, "recent_total": 5},
        }

        context = service._build_prompt_context(data, student_user)

        assert "Test Student" in context
        assert "Fractions" in context
        assert "90%" in context or "0.9" in context
        assert "Decimals" in context
        assert "Grade 5" in context

    @pytest.mark.asyncio
    async def test_report_with_risk_indicators(self) -> None:
        session = AsyncMock()
        service = ReportService(session)
        parent_user = Mock(spec=User)
        parent_user.id = "parent-1"
        parent_user.role = UserRole.PARENT

        profile = Mock(spec=StudentProfile)
        profile.id = "sp-1"
        profile.user_id = "student-user-1"
        profile.grade_level = "Grade 5"
        profile.current_streak_days = 0
        profile.avg_session_duration_minutes = 5

        student_user = Mock(spec=User)
        student_user.full_name = "At Risk Student"

        service._verify_parent_access = AsyncMock(return_value=profile)
        service.user_repo.get = AsyncMock(return_value=student_user)
        service._collect_student_data = AsyncMock(
            return_value={
                "profile": {"grade_level": "Grade 5", "current_streak_days": 0, "avg_session_duration_minutes": 5},
                "progress": {"total_lessons": 20, "completed_lessons": 2, "in_progress_lessons": 1},
                "mastery": {"total_concepts": 5, "mastered_concepts": 0, "average_mastery": 0.15, "concepts": []},
                "misconceptions": [
                    {"concept_title": "Fractions", "category": "conceptual", "description": "Fundamental misunderstanding", "frequency": 5},
                ],
                "knowledge_gaps": [],
                "pacing": [{"course_title": "Math 101", "current_week": 6, "target_lessons_per_week": 3, "pace_status": "behind"}],
                "sessions": {"total": 1, "recent": []},
                "attempts": {"total": 2, "recent_correct": 0, "recent_total": 2},
            }
        )

        ai_data = {
            "title": "Weekly Update - Needs Attention",
            "executive_summary": "Student is significantly behind.",
            "strengths": [{"description": "Continues to show up", "category": "engagement", "evidence": []}],
            "challenges": [{"description": "Far behind in all concepts", "category": "conceptual", "severity": "high", "concept_title": None}],
            "recommendations": [{"description": "Immediate intervention needed", "priority": "high", "category": "structure"}],
            "risk_indicators": [
                {"risk_type": "pacing", "description": "Falling behind schedule", "severity": "high", "actionable": True},
                {"risk_type": "engagement", "description": "Very low engagement", "severity": "high", "actionable": True},
            ],
        }

        with patch.object(service.gemini, "generate_json", AsyncMock(return_value=ai_data)):
            async def _mock_refresh(report):
                report.id = "rpt-risk"
                report.is_read = False
                report.created_at = None

            session.refresh = AsyncMock(side_effect=_mock_refresh)

            result = await service.generate_report(parent_user, "sp-1", "weekly")

        assert result.report_data is not None
        assert len(result.report_data.risk_indicators) == 2
        assert result.report_data.risk_indicators[0].severity == "high"
