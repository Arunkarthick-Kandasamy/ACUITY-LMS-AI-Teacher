from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.ai.services.gemini import GeminiService
from app.common.exceptions import ForbiddenException, NotFoundException
from app.common.types import EnrollmentStatus, LessonProgressStatus, UserRole
from app.curriculum.models import Concept, Course, Lesson, Module
from app.diagnosis.models import Misconception
from app.enrollment.models import CourseSchedule, StudentCourseEnrollment
from app.enrollment.repository import CourseScheduleRepository, EnrollmentRepository
from app.mastery.models import MasteryRecord
from app.mastery.repository import MasteryRecordRepository
from app.progress.repository import LessonProgressRepository
from app.teaching.models import Attempt, TeachingSession
from app.users.models import ParentStudentLink, StudentProfile, User
from app.users.repository import StudentProfileRepository, UserRepository

from .models import Report
from .prompts import REPORT_GENERATION_PROMPT, SYSTEM_REPORT_GENERATION
from .schemas import (
    ChallengeItem,
    RecommendationItem,
    ReportData,
    ReportListItem,
    ReportResponse,
    RiskIndicator,
    StrengthItem,
)

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.student_profile_repo = StudentProfileRepository(session)
        self.user_repo = UserRepository(session)
        self.mastery_repo = MasteryRecordRepository(session)
        self.progress_repo = LessonProgressRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.schedule_repo = CourseScheduleRepository(session)
        self.gemini = GeminiService()

    async def _verify_parent_access(
        self, current_user: User, student_id: str
    ) -> StudentProfile:
        if current_user.role == UserRole.ADMIN:
            profile = await self.student_profile_repo.get(student_id)
            if profile is None:
                raise NotFoundException(message="Student not found")
            return profile

        if current_user.role != UserRole.PARENT:
            raise ForbiddenException(
                message="Only parents and admins can access student reports"
            )

        stmt = select(ParentStudentLink).where(
            ParentStudentLink.parent_id == current_user.id,
            ParentStudentLink.student_id == student_id,
        )
        result = await self.session.execute(stmt)
        link = result.unique().scalar_one_or_none()
        if link is None:
            raise ForbiddenException(
                message="You are not linked to this student"
            )
        return link.student

    async def generate_report(
        self, current_user: User, student_id: str, report_type: str = "weekly"
    ) -> ReportResponse:
        profile = await self._verify_parent_access(current_user, student_id)
        student_user = await self.user_repo.get(profile.user_id)
        if student_user is None:
            raise NotFoundException(message="Student user not found")

        data = await self._collect_student_data(profile)
        context = self._build_prompt_context(data, student_user)
        report_data = await self._generate_with_ai(context)

        now = datetime.now(timezone.utc)
        report = Report(
            student_id=profile.id,
            parent_id=current_user.id if current_user.role == UserRole.PARENT else None,
            report_type=report_type,
            title=report_data.get("title", "Learning Progress Report"),
            summary=report_data.get("executive_summary", ""),
            recommendations=report_data.get("recommendations", []),
            report_data=report_data,
            generated_at=now,
        )
        self.session.add(report)
        await self.session.flush()
        await self.session.refresh(report)

        return await self._to_response(report)

    async def get_report(self, current_user: User, report_id: str) -> ReportResponse:
        stmt = select(Report).where(Report.id == report_id)
        result = await self.session.execute(stmt)
        report = result.unique().scalar_one_or_none()
        if report is None:
            raise NotFoundException(message="Report not found")

        await self._verify_parent_access(current_user, report.student_id)

        return await self._to_response(report)

    async def get_student_reports(
        self,
        current_user: User,
        student_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[ReportListItem], int]:
        profile = await self._verify_parent_access(current_user, student_id)

        stmt = (
            select(Report)
            .where(Report.student_id == profile.id)
            .order_by(Report.generated_at.desc())
        )
        count_stmt = (
            select(func.count())
            .select_from(Report)
            .where(Report.student_id == profile.id)
        )
        total = await self.session.scalar(count_stmt) or 0

        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        result = await self.session.execute(stmt)
        reports = result.unique().scalars().all()

        items = [_report_list_item(r) for r in reports]
        return items, total

    async def _collect_student_data(self, profile: StudentProfile) -> dict[str, Any]:
        data: dict[str, Any] = {
            "profile": {
                "grade_level": profile.grade_level,
                "current_streak_days": profile.current_streak_days,
                "avg_session_duration_minutes": profile.avg_session_duration_minutes,
            },
            "progress": {"total_lessons": 0, "completed_lessons": 0, "in_progress_lessons": 0},
            "mastery": {"total_concepts": 0, "mastered_concepts": 0, "average_mastery": 0.0, "concepts": []},
            "misconceptions": [],
            "knowledge_gaps": [],
            "pacing": [],
            "sessions": {"total": 0, "recent": []},
            "attempts": {"total": 0, "recent_correct": 0, "recent_total": 0},
        }

        progresses = await self.progress_repo.find_by_student(profile.id)
        completed = sum(1 for p in progresses if p.status == LessonProgressStatus.COMPLETED)
        in_progress = sum(1 for p in progresses if p.status == LessonProgressStatus.IN_PROGRESS)
        data["progress"] = {
            "total_lessons": len(progresses),
            "completed_lessons": completed,
            "in_progress_lessons": in_progress,
        }

        records = await self.mastery_repo.find_by_student(profile.id)
        mastered = sum(1 for r in records if r.mastery_level >= 0.8)
        avg = round(sum(r.mastery_level for r in records) / len(records), 4) if records else 0.0
        concepts_data = []
        for r in records:
            concept_title = r.concept.title if hasattr(r, "concept") and r.concept else None
            concepts_data.append({
                "concept_id": r.concept_id,
                "title": concept_title,
                "mastery_level": r.mastery_level,
                "total_attempts": r.total_attempts,
            })
        data["mastery"] = {
            "total_concepts": len(records),
            "mastered_concepts": mastered,
            "average_mastery": avg,
            "concepts": concepts_data,
        }

        misconception_stmt = (
            select(Misconception)
            .where(
                Misconception.student_id == profile.id,
                Misconception.is_resolved.is_(False),
            )
            .options(joinedload(Misconception.concept))
        )
        mc_result = await self.session.execute(misconception_stmt)
        misconceptions = mc_result.unique().scalars().all()
        data["misconceptions"] = [
            {
                "concept_title": m.concept.title if hasattr(m, "concept") and m.concept else None,
                "category": m.category.value if hasattr(m.category, "value") else str(m.category),
                "description": m.description,
                "frequency": m.frequency,
            }
            for m in misconceptions
        ]

        enrollments = await self.enrollment_repo.find_by_student(profile.id)
        pacing_data = []
        for enrollment in enrollments:
            schedule = await self.schedule_repo.find_by_enrollment(enrollment.id)
            if schedule is None:
                continue
            course_stmt = select(Course).where(Course.id == enrollment.course_id)
            course_result = await self.session.execute(course_stmt)
            course = course_result.unique().scalar_one_or_none()
            pacing_data.append({
                "course_title": course.title if course else None,
                "current_week": schedule.current_week,
                "target_lessons_per_week": schedule.target_lessons_per_week,
                "pace_status": schedule.pace_status.value if hasattr(schedule.pace_status, "value") else str(schedule.pace_status),
            })
        data["pacing"] = pacing_data

        session_stmt = (
            select(TeachingSession)
            .where(TeachingSession.student_id == profile.id)
            .order_by(TeachingSession.last_activity_at.desc())
            .limit(10)
        )
        session_result = await self.session.execute(session_stmt)
        sessions = session_result.unique().scalars().all()
        data["sessions"] = {
            "total": len(sessions),
            "recent": [
                {
                    "state": s.state.value if hasattr(s.state, "value") else str(s.state),
                    "last_activity_at": s.last_activity_at.isoformat() if s.last_activity_at else None,
                }
                for s in sessions
            ],
        }

        attempt_stmt = (
            select(Attempt)
            .where(Attempt.student_id == profile.id)
            .order_by(Attempt.attempted_at.desc())
            .limit(20)
        )
        attempt_result = await self.session.execute(attempt_stmt)
        attempts = attempt_result.unique().scalars().all()
        recent_correct = sum(1 for a in attempts if a.is_correct)
        data["attempts"] = {
            "total": len(attempts),
            "recent_correct": recent_correct,
            "recent_total": len(attempts),
        }

        return data

    def _build_prompt_context(
        self, data: dict[str, Any], student_user: User
    ) -> str:
        lines = [
            f"Student: {student_user.full_name}",
            f"Grade Level: {data['profile'].get('grade_level', 'N/A')}",
            f"Current Streak: {data['profile'].get('current_streak_days', 0)} days",
            f"Avg Session Duration: {data['profile'].get('avg_session_duration_minutes', 0)} minutes",
            "",
            "--- Progress ---",
            f"Total Lessons: {data['progress']['total_lessons']}",
            f"Completed: {data['progress']['completed_lessons']}",
            f"In Progress: {data['progress']['in_progress_lessons']}",
            "",
            "--- Mastery ---",
            f"Total Concepts: {data['mastery']['total_concepts']}",
            f"Mastered (>=80%): {data['mastery']['mastered_concepts']}",
            f"Average Mastery: {data['mastery']['average_mastery']:.1%}",
        ]
        if data["mastery"]["concepts"]:
            lines.append("Concept Mastery Details:")
            for c in data["mastery"]["concepts"]:
                lines.append(
                    f"  - {c['title'] or 'Unknown'}: {c['mastery_level']:.0%} mastery, "
                    f"{c['total_attempts']} attempts"
                )

        lines.append("")
        lines.append("--- Active Misconceptions ---")
        if data["misconceptions"]:
            for m in data["misconceptions"]:
                lines.append(
                    f"  - [{m['category']}] {m['description']} "
                    f"(concept: {m['concept_title'] or 'N/A'}, frequency: {m['frequency']})"
                )
        else:
            lines.append("  None")

        lines.append("")
        lines.append("--- Pacing ---")
        if data["pacing"]:
            for p in data["pacing"]:
                lines.append(
                    f"  - {p['course_title'] or 'Course'}: Week {p['current_week']}, "
                    f"Status: {p['pace_status']}"
                )
        else:
            lines.append("  No active enrollments")

        lines.append("")
        lines.append("--- Recent Sessions ---")
        lines.append(f"Total recent sessions: {data['sessions']['total']}")
        for s in data["sessions"]["recent"]:
            lines.append(f"  - State: {s['state']}")

        lines.append("")
        lines.append("--- Recent Attempts ---")
        lines.append(f"Recent total: {data['attempts']['recent_total']}")
        lines.append(f"Recent correct: {data['attempts']['recent_correct']}")

        return "\n".join(lines)

    async def _generate_with_ai(self, context: str) -> dict[str, Any]:
        prompt = REPORT_GENERATION_PROMPT.format(student_data=context)
        try:
            result = await self.gemini.generate_json(prompt, SYSTEM_REPORT_GENERATION)
            return self._validate_report_data(result)
        except Exception as e:
            logger.warning("Gemini report generation failed, using fallback: %s", e)
            return self._fallback_report_data(context)

    def _validate_report_data(self, data: dict[str, Any]) -> dict[str, Any]:
        validated: dict[str, Any] = {
            "title": str(data.get("title", "Learning Progress Report")),
            "executive_summary": str(data.get("executive_summary", "")),
            "strengths": [],
            "challenges": [],
            "recommendations": [],
            "risk_indicators": [],
        }

        for s in data.get("strengths", []):
            if isinstance(s, dict) and s.get("description"):
                validated["strengths"].append({
                    "description": str(s["description"]),
                    "category": str(s.get("category", "academic")),
                    "evidence": list(s.get("evidence", [])),
                })

        for c in data.get("challenges", []):
            if isinstance(c, dict) and c.get("description"):
                validated["challenges"].append({
                    "description": str(c["description"]),
                    "category": str(c.get("category", "conceptual")),
                    "severity": str(c.get("severity", "medium")),
                    "concept_title": str(c["concept_title"]) if c.get("concept_title") else None,
                })

        for r in data.get("recommendations", []):
            if isinstance(r, dict) and r.get("description"):
                validated["recommendations"].append({
                    "description": str(r["description"]),
                    "priority": str(r.get("priority", "medium")),
                    "category": str(r.get("category", "practice")),
                })

        for ri in data.get("risk_indicators", []):
            if isinstance(ri, dict) and ri.get("risk_type") and ri.get("description"):
                validated["risk_indicators"].append({
                    "risk_type": str(ri["risk_type"]),
                    "description": str(ri["description"]),
                    "severity": str(ri.get("severity", "medium")),
                    "actionable": bool(ri.get("actionable", True)),
                })

        return validated

    def _fallback_report_data(self, context: str) -> dict[str, Any]:
        return {
            "title": "Weekly Learning Progress Report",
            "executive_summary": "This report provides an overview of the student's recent learning activities, "
                                "mastery progress, and areas that may need additional attention.",
            "strengths": [
                {
                    "description": "The student is actively engaged in learning sessions",
                    "category": "engagement",
                    "evidence": ["Recent teaching sessions detected"],
                }
            ],
            "challenges": [
                {
                    "description": "Some concepts may need additional practice to reach mastery",
                    "category": "conceptual",
                    "severity": "medium",
                    "concept_title": None,
                }
            ],
            "recommendations": [
                {
                    "description": "Encourage regular practice sessions to reinforce learning",
                    "priority": "medium",
                    "category": "practice",
                }
            ],
            "risk_indicators": [],
        }

    async def _to_response(self, report: Report) -> ReportResponse:
        report_data = None
        if report.report_data:
            try:
                report_data = ReportData(
                    title=report.report_data.get("title", report.title or "Learning Progress Report"),
                    executive_summary=report.report_data.get("executive_summary", report.summary or ""),
                    strengths=[
                        StrengthItem(**s) for s in report.report_data.get("strengths", [])
                    ],
                    challenges=[
                        ChallengeItem(**c) for c in report.report_data.get("challenges", [])
                    ],
                    recommendations=[
                        RecommendationItem(**r) for r in report.report_data.get("recommendations", report.recommendations or [])
                    ],
                    risk_indicators=[
                        RiskIndicator(**ri) for ri in report.report_data.get("risk_indicators", [])
                    ],
                )
            except Exception:
                report_data = None

        return ReportResponse(
            id=report.id,
            student_id=report.student_id,
            parent_id=report.parent_id,
            report_type=report.report_type.value if hasattr(report.report_type, "value") else str(report.report_type),
            title=report.title,
            generated_at=report.generated_at,
            summary=report.summary,
            recommendations=report.recommendations or [],
            report_data=report_data,
            is_read=report.is_read,
            created_at=report.created_at,
        )


def _report_list_item(report: Report) -> ReportListItem:
    return ReportListItem(
        id=report.id,
        student_id=report.student_id,
        report_type=report.report_type.value if hasattr(report.report_type, "value") else str(report.report_type),
        title=report.title,
        generated_at=report.generated_at,
        summary=report.summary,
        is_read=report.is_read,
        created_at=report.created_at,
    )
