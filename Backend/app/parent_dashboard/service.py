from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.common.exceptions import ForbiddenException, NotFoundException
from app.common.types import EnrollmentStatus, LessonProgressStatus, UserRole
from app.curriculum.models import Concept, Course, Lesson, Module
from app.enrollment.models import CourseSchedule, StudentCourseEnrollment
from app.enrollment.repository import CourseScheduleRepository, EnrollmentRepository
from app.mastery.models import MasteryRecord
from app.mastery.repository import MasteryRecordRepository
from app.progress.repository import LessonProgressRepository
from app.teaching.models import Attempt, LessonProgress, TeachingSession
from app.users.models import ParentStudentLink, StudentProfile, User
from app.users.repository import StudentProfileRepository, UserRepository

from .repository import (
    MisconceptionRepository,
    ParentStudentLinkRepository,
    ParentTeachingSessionRepository,
)
from .schemas import (
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


class ParentDashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.parent_link_repo = ParentStudentLinkRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)
        self.user_repo = UserRepository(session)
        self.mastery_repo = MasteryRecordRepository(session)
        self.progress_repo = LessonProgressRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.schedule_repo = CourseScheduleRepository(session)
        self.misconception_repo = MisconceptionRepository(session)
        self.session_repo = ParentTeachingSessionRepository(session)

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
                message="Only parents and admins can access student data"
            )

        link = await self.parent_link_repo.find_by_parent_and_student(
            current_user.id, student_id
        )
        if link is None:
            raise ForbiddenException(
                message="You are not linked to this student"
            )
        return link.student

    async def get_linked_students(self, current_user: User) -> list[ParentStudentResponse]:
        if current_user.role == UserRole.ADMIN:
            profiles = await self.student_profile_repo.find()
            result = []
            for profile in profiles:
                user = await self.user_repo.get(profile.user_id)
                result.append(
                    ParentStudentResponse(
                        student_id=profile.id,
                        full_name=user.full_name if user else "Unknown",
                        grade_level=profile.grade_level,
                        current_streak_days=profile.current_streak_days,
                    )
                )
            return result

        links = await self.parent_link_repo.find_by_parent(current_user.id)
        result = []
        for link in links:
            user = await self.user_repo.get(link.student.user_id)
            result.append(
                ParentStudentResponse(
                    student_id=link.student_id,
                    full_name=user.full_name if user else "Unknown",
                    grade_level=link.student.grade_level,
                    current_streak_days=link.student.current_streak_days,
                )
            )
        return result

    async def get_student_profile(
        self, current_user: User, student_id: str
    ) -> StudentProfileResponse:
        profile = await self._verify_parent_access(current_user, student_id)
        user = await self.user_repo.get(profile.user_id)
        if user is None:
            raise NotFoundException(message="User not found for student profile")

        return StudentProfileResponse(
            student_id=profile.id,
            full_name=user.full_name,
            email=user.email,
            grade_level=profile.grade_level,
            current_streak_days=profile.current_streak_days,
            avg_session_duration_minutes=profile.avg_session_duration_minutes,
            created_at=profile.created_at,
        )

    async def get_progress_summary(
        self, current_user: User, student_id: str
    ) -> ProgressSummaryResponse:
        profile = await self._verify_parent_access(current_user, student_id)
        progresses = await self.progress_repo.find_by_student(profile.id)

        total = len(progresses)
        completed = sum(
            1 for p in progresses if p.status == LessonProgressStatus.COMPLETED
        )
        in_progress = sum(
            1 for p in progresses if p.status == LessonProgressStatus.IN_PROGRESS
        )
        not_started = sum(
            1 for p in progresses if p.status == LessonProgressStatus.NOT_STARTED
        )
        completion_pct = round((completed / total * 100) if total > 0 else 0.0, 1)

        return ProgressSummaryResponse(
            total_lessons=total,
            completed_lessons=completed,
            in_progress_lessons=in_progress,
            not_started_lessons=not_started,
            completion_percentage=completion_pct,
        )

    async def get_curriculum_tree(
        self, current_user: User, student_id: str, course_id: str
    ) -> CurriculumTreeResponse:
        profile = await self._verify_parent_access(current_user, student_id)

        stmt = (
            select(Course)
            .where(Course.id == course_id)
            .options(
                joinedload(Course.modules).joinedload(Module.lessons).joinedload(Lesson.concepts)
            )
        )
        result = await self.session.execute(stmt)
        course = result.unique().scalar_one_or_none()
        if course is None:
            raise NotFoundException(message="Course not found")

        modules = []
        for mod in sorted(course.modules, key=lambda m: m.order_index):
            lessons_data = []
            for les in sorted(mod.lessons, key=lambda l: l.order_index):
                progress = None
                for p in await self.progress_repo.find_by_student(profile.id):
                    if p.lesson_id == les.id:
                        progress = p
                        break

                lessons_data.append({
                    "lesson_id": les.id,
                    "lesson_title": les.title,
                    "order_index": les.order_index,
                    "estimated_duration_minutes": les.estimated_duration_minutes,
                    "is_required": les.is_required,
                    "status": progress.status.value if progress else LessonProgressStatus.NOT_STARTED.value,
                    "completion_percentage": progress.completion_percentage if progress else 0.0,
                    "concept_count": len(les.concepts),
                })

            modules.append(
                CurriculumNode(
                    module_id=mod.id,
                    module_title=mod.title,
                    module_order=mod.order_index,
                    lessons=lessons_data,
                )
            )

        return CurriculumTreeResponse(
            course_id=course.id,
            course_title=course.title,
            modules=modules,
        )

    async def get_mastery_summary(
        self, current_user: User, student_id: str
    ) -> MasterySummaryResponse:
        profile = await self._verify_parent_access(current_user, student_id)
        records = await self.mastery_repo.find_by_student(profile.id)

        total = len(records)
        mastered = sum(1 for r in records if r.mastery_level >= 0.8)
        in_progress = sum(
            1 for r in records if 0.0 < r.mastery_level < 0.8
        )
        not_started = sum(1 for r in records if r.mastery_level <= 0.0)
        avg = round(sum(r.mastery_level for r in records) / total, 4) if total > 0 else 0.0

        concepts = []
        for r in records:
            concept_title = r.concept.title if hasattr(r, "concept") and r.concept else None
            lesson_title = None
            if r.concept and r.concept.lesson:
                lesson_title = r.concept.lesson.title

            concepts.append(
                MasteryConceptResponse(
                    concept_id=r.concept_id,
                    concept_title=concept_title,
                    lesson_title=lesson_title,
                    mastery_level=r.mastery_level,
                    total_attempts=r.total_attempts,
                    consecutive_correct=r.consecutive_correct,
                    last_attempted_at=r.last_attempted_at,
                )
            )

        return MasterySummaryResponse(
            total_concepts=total,
            mastered_concepts=mastered,
            in_progress_concepts=in_progress,
            not_started_concepts=not_started,
            average_mastery=avg,
            concepts=concepts,
        )

    async def get_mastery_by_concepts(
        self, current_user: User, student_id: str
    ) -> list[MasteryConceptResponse]:
        summary = await self.get_mastery_summary(current_user, student_id)
        return summary.concepts

    async def get_pacing(
        self, current_user: User, student_id: str
    ) -> list[PacingStatusResponse]:
        profile = await self._verify_parent_access(current_user, student_id)
        enrollments = await self.enrollment_repo.find_by_student(profile.id)

        result = []
        for enrollment in enrollments:
            schedule = await self.schedule_repo.find_by_enrollment(enrollment.id)
            if schedule is None:
                continue

            stmt = select(Course).where(Course.id == enrollment.course_id)
            course_result = await self.session.execute(stmt)
            course = course_result.unique().scalar_one_or_none()

            result.append(
                PacingStatusResponse(
                    enrollment_id=enrollment.id,
                    course_id=enrollment.course_id,
                    course_title=course.title if course else None,
                    current_week=schedule.current_week,
                    target_lessons_per_week=schedule.target_lessons_per_week,
                    pace_status=schedule.pace_status.value
                    if hasattr(schedule.pace_status, "value")
                    else str(schedule.pace_status),
                    last_pacing_adjustment_at=schedule.last_pacing_adjustment_at,
                )
            )

        return result

    async def get_misconceptions(
        self, current_user: User, student_id: str
    ) -> list[MisconceptionResponse]:
        profile = await self._verify_parent_access(current_user, student_id)
        records = await self.misconception_repo.find_active_by_student(profile.id)

        result = []
        for m in records:
            concept_title = m.concept.title if hasattr(m, "concept") and m.concept else None
            result.append(
                MisconceptionResponse(
                    misconception_id=m.id,
                    concept_id=m.concept_id,
                    concept_title=concept_title,
                    category=m.category.value if hasattr(m.category, "value") else str(m.category),
                    description=m.description,
                    detected_at=m.detected_at,
                    frequency=m.frequency,
                    is_resolved=m.is_resolved,
                    resolved_at=m.resolved_at,
                )
            )
        return result

    async def get_knowledge_gaps(
        self, current_user: User, student_id: str
    ) -> list[KnowledgeGapResponse]:
        profile = await self._verify_parent_access(current_user, student_id)
        records = await self.misconception_repo.find_knowledge_gaps(profile.id)

        result = []
        for m in records:
            concept_title = m.concept.title if hasattr(m, "concept") and m.concept else None
            result.append(
                KnowledgeGapResponse(
                    gap_id=m.id,
                    concept_id=m.concept_id,
                    concept_title=concept_title,
                    description=m.description,
                    detected_at=m.detected_at,
                    frequency=m.frequency,
                )
            )
        return result

    async def get_sessions(
        self,
        current_user: User,
        student_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[TeachingSessionResponse], int]:
        profile = await self._verify_parent_access(current_user, student_id)
        sessions, total = await self.session_repo.find_by_student(
            profile.id, offset=offset, limit=limit
        )

        result = []
        for s in sessions:
            course_title = None
            concept_title = None

            stmt = select(Course).where(Course.id == s.course_id)
            course_result = await self.session.execute(stmt)
            course = course_result.unique().scalar_one_or_none()
            if course:
                course_title = course.title

            if s.current_concept_id:
                concept_stmt = select(Concept).where(Concept.id == s.current_concept_id)
                concept_result = await self.session.execute(concept_stmt)
                concept = concept_result.unique().scalar_one_or_none()
                if concept:
                    concept_title = concept.title

            result.append(
                TeachingSessionResponse(
                    session_id=s.id,
                    course_id=s.course_id,
                    course_title=course_title,
                    concept_title=concept_title,
                    state=s.state.value if hasattr(s.state, "value") else str(s.state),
                    started_at=s.started_at,
                    last_activity_at=s.last_activity_at,
                    completed_at=s.completed_at,
                )
            )

        return result, total

    async def get_recent_activity(
        self, current_user: User, student_id: str, days: int = 7
    ) -> list[RecentActivityItem]:
        profile = await self._verify_parent_access(current_user, student_id)
        items: list[RecentActivityItem] = []

        sessions = await self.session_repo.find_recent_by_student(
            profile.id, days=days
        )
        for s in sessions:
            concept_title = None
            if s.current_concept_id:
                concept_stmt = select(Concept).where(Concept.id == s.current_concept_id)
                concept_result = await self.session.execute(concept_stmt)
                concept = concept_result.unique().scalar_one_or_none()
                if concept:
                    concept_title = concept.title

            items.append(
                RecentActivityItem(
                    activity_type="session",
                    description=f"Teaching session ({s.state.value if hasattr(s.state, 'value') else str(s.state)})",
                    timestamp=s.last_activity_at,
                    session_id=s.id,
                    concept_title=concept_title,
                )
            )

        attempts_stmt = (
            select(Attempt)
            .where(Attempt.student_id == profile.id)
            .order_by(Attempt.attempted_at.desc())
            .limit(10)
        )
        attempts_result = await self.session.execute(attempts_stmt)
        attempts = attempts_result.unique().scalars().all()

        for a in attempts:
            items.append(
                RecentActivityItem(
                    activity_type="attempt",
                    description=f"Exercise attempt ({'correct' if a.is_correct else 'incorrect'}, score: {a.score})",
                    timestamp=a.attempted_at,
                    session_id=a.teaching_session_id,
                )
            )

        misconceptions = await self.misconception_repo.find_active_by_student(
            profile.id
        )
        for m in misconceptions[:5]:
            concept_title = m.concept.title if hasattr(m, "concept") and m.concept else None
            items.append(
                RecentActivityItem(
                    activity_type="misconception",
                    description=f"Misconception detected: {m.description[:100]}",
                    timestamp=m.detected_at,
                    concept_title=concept_title,
                )
            )

        items.sort(key=lambda x: x.timestamp or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return items[:20]

    async def get_dashboard(
        self, current_user: User, student_id: str
    ) -> DashboardResponse:
        profile = await self._verify_parent_access(current_user, student_id)
        user = await self.user_repo.get(profile.user_id)

        progress = await self.get_progress_summary(current_user, student_id)
        mastery = await self.get_mastery_summary(current_user, student_id)
        misconceptions = await self.get_misconceptions(current_user, student_id)
        knowledge_gaps = await self.get_knowledge_gaps(current_user, student_id)
        pacing = await self.get_pacing(current_user, student_id)
        sessions_result, _ = await self.get_sessions(
            current_user, student_id, offset=0, limit=5
        )
        recent_activity = await self.get_recent_activity(current_user, student_id)
        completion_forecast = await self._compute_completion_forecast(
            student_id, profile.id
        )

        return DashboardResponse(
            student=StudentProfileResponse(
                student_id=profile.id,
                full_name=user.full_name if user else "Unknown",
                email=user.email if user else "",
                grade_level=profile.grade_level,
                current_streak_days=profile.current_streak_days,
                avg_session_duration_minutes=profile.avg_session_duration_minutes,
                created_at=profile.created_at,
            ),
            progress=progress,
            mastery=mastery,
            active_misconceptions=misconceptions,
            knowledge_gaps=knowledge_gaps,
            pacing=pacing,
            recent_sessions=sessions_result,
            recent_activity=recent_activity,
            learning_streak_days=profile.current_streak_days,
            completion_forecast=completion_forecast,
        )

    async def _compute_completion_forecast(
        self, student_id: str, profile_id: str
    ) -> dict[str, Any]:
        enrollments = await self.enrollment_repo.find_by_student(profile_id)
        if not enrollments:
            return {"estimated_completion": None, "on_track": True}

        forecast = {}
        for enrollment in enrollments:
            schedule = await self.schedule_repo.find_by_enrollment(enrollment.id)
            if schedule is None:
                continue

            stmt = select(Course).where(Course.id == enrollment.course_id)
            course_result = await self.session.execute(stmt)
            course = course_result.unique().scalar_one_or_none()
            if course is None:
                continue

            stmt = select(func.count(Lesson.id)).where(
                Lesson.module_id.in_(
                    select(Module.id).where(Module.course_id == course.id).subquery()
                )
            )
            total_lessons_result = await self.session.execute(stmt)
            total_lessons = total_lessons_result.scalar() or 1

            progresses = await self.progress_repo.find_by_student(profile_id)
            completed = sum(
                1 for p in progresses if p.status == LessonProgressStatus.COMPLETED
            )

            completed_pct = round((completed / total_lessons) * 100, 1) if total_lessons > 0 else 0.0
            pace_status = schedule.pace_status.value if hasattr(schedule.pace_status, "value") else str(schedule.pace_status)

            forecast[enrollment.course_id] = {
                "course_title": course.title,
                "total_lessons": total_lessons,
                "completed_lessons": completed,
                "completion_percentage": completed_pct,
                "current_week": schedule.current_week,
                "pace_status": pace_status,
            }

        return forecast
