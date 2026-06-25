from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.assessments.models import (
    Assessment,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResponse,
    QuestionBank,
)
from app.assessments.repository import (
    AssessmentAttemptRepository,
    AssessmentQuestionRepository,
    AssessmentRepository,
    AssessmentResponseRepository,
    QuestionBankRepository,
)
from app.common.exceptions import NotFoundException, ValidationException
from app.common.types import AssessmentType, LessonProgressStatus, QuestionType
from sqlalchemy import select as _select

from app.curriculum.models import Concept, Exercise, Lesson, Module
from app.curriculum.repository import CourseRepository, LessonRepository
from app.enrollment.repository import CourseScheduleRepository, EnrollmentRepository
from app.mastery.repository import MasteryRecordRepository
from app.mastery.service import MasteryService
from app.progress.repository import LessonProgressRepository
from app.progress.service import ProgressService
from app.users.models import StudentProfile
from app.users.repository import StudentProfileRepository


class AssessmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)
        self.question_repo = AssessmentQuestionRepository(session)
        self.attempt_repo = AssessmentAttemptRepository(session)
        self.response_repo = AssessmentResponseRepository(session)
        self.bank_repo = QuestionBankRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)
        self.progress_repo = LessonProgressRepository(session)
        self.mastery_repo = MasteryRecordRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.schedule_repo = CourseScheduleRepository(session)
        self.course_repo = CourseRepository(session)
        self.lesson_repo = LessonRepository(session)
        self.progress_service = ProgressService(session)
        self.mastery_service = MasteryService(session)

    async def _get_student_profile(self, user_id: str) -> StudentProfile:
        profile = await self.student_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundException(message="Student profile not found")
        return profile

    async def _get_assessment(self, assessment_id: str) -> Assessment:
        assessment = await self.assessment_repo.get(assessment_id)
        if assessment is None:
            raise NotFoundException(message="Assessment not found")
        return assessment

    # ------------------------------------------------------------------
    # Admin: Assessment CRUD
    # ------------------------------------------------------------------

    async def create_assessment(
        self, user_id: str, **kwargs: Any
    ) -> Assessment:
        try:
            assessment_type = AssessmentType(kwargs.get("assessment_type", ""))
        except ValueError:
            raise ValidationException(message=f"Invalid assessment type: {kwargs.get('assessment_type')}")

        return await self.assessment_repo.create(
            created_by=user_id,
            assessment_type=assessment_type,
            **{k: v for k, v in kwargs.items() if k != "assessment_type"},
        )

    async def update_assessment(
        self, assessment_id: str, **kwargs: Any
    ) -> Assessment:
        assessment = await self._get_assessment(assessment_id)
        if kwargs.get("assessment_type"):
            try:
                AssessmentType(kwargs["assessment_type"])
            except ValueError:
                raise ValidationException(message=f"Invalid assessment type: {kwargs['assessment_type']}")
        updated = await self.assessment_repo.update(assessment_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Assessment not found")
        return updated

    async def delete_assessment(self, assessment_id: str) -> None:
        assessment = await self._get_assessment(assessment_id)
        await self.assessment_repo.delete(assessment.id)

    async def get_assessment(self, assessment_id: str) -> Assessment:
        return await self._get_assessment(assessment_id)

    async def get_all_assessments(self) -> list[Assessment]:
        return await self.assessment_repo.find()

    async def get_assessments_by_course(self, course_id: str) -> list[Assessment]:
        return await self.assessment_repo.find_by_course(course_id)

    # ------------------------------------------------------------------
    # Admin: Question CRUD
    # ------------------------------------------------------------------

    async def create_question(self, **kwargs: Any) -> AssessmentQuestion:
        assessment_id = kwargs.get("assessment_id")
        if not assessment_id:
            raise ValidationException(message="assessment_id is required")
        await self._get_assessment(assessment_id)
        try:
            QuestionType(kwargs.get("question_type", ""))
        except ValueError:
            raise ValidationException(message=f"Invalid question type: {kwargs.get('question_type')}")
        return await self.question_repo.create(**kwargs)

    async def update_question(self, question_id: str, **kwargs: Any) -> AssessmentQuestion:
        question = await self.question_repo.get(question_id)
        if question is None:
            raise NotFoundException(message="Question not found")
        if kwargs.get("question_type"):
            try:
                QuestionType(kwargs["question_type"])
            except ValueError:
                raise ValidationException(message=f"Invalid question type: {kwargs['question_type']}")
        updated = await self.question_repo.update(question_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Question not found")
        return updated

    async def delete_question(self, question_id: str) -> None:
        question = await self.question_repo.get(question_id)
        if question is None:
            raise NotFoundException(message="Question not found")
        await self.question_repo.delete(question.id)

    async def get_questions(self, assessment_id: str) -> list[AssessmentQuestion]:
        return await self.question_repo.find_by_assessment(assessment_id)

    # ------------------------------------------------------------------
    # Student: Available assessments
    # ------------------------------------------------------------------

    async def get_available_assessments(self, user_id: str) -> list[Assessment]:
        profile = await self._get_student_profile(user_id)
        enrollments = await self.enrollment_repo.find_by_student(profile.id)
        course_ids = [e.course_id for e in enrollments]
        all_published = await self.assessment_repo.find_published()
        return [a for a in all_published if a.course_id in course_ids]

    async def get_assessment_detail(self, assessment_id: str) -> Assessment:
        return await self._get_assessment(assessment_id)

    # ------------------------------------------------------------------
    # Student: Attempt flow
    # ------------------------------------------------------------------

    async def start_attempt(self, assessment_id: str, user_id: str) -> dict[str, Any]:
        assessment = await self._get_assessment(assessment_id)
        if not assessment.is_published:
            raise ValidationException(message="Assessment is not published")
        profile = await self._get_student_profile(user_id)

        max_num = await self.attempt_repo.get_max_attempt_number(
            assessment_id, profile.id
        )
        if max_num >= assessment.max_attempts:
            raise ValidationException(
                message=f"Maximum attempts ({assessment.max_attempts}) reached"
            )

        attempt = await self.attempt_repo.create(
            assessment_id=assessment_id,
            student_id=profile.id,
            attempt_number=max_num + 1,
            started_at=datetime.now(timezone.utc),
        )

        questions = await self.question_repo.find_by_assessment(assessment_id)
        question_list = [
            {
                "id": q.id,
                "question_type": q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
                "prompt": q.prompt,
                "options": q.options,
                "difficulty": q.difficulty,
                "marks": q.marks,
                "order_index": q.order_index,
            }
            for q in questions
        ]

        return {
            "attempt_id": attempt.id,
            "assessment_id": assessment_id,
            "started_at": attempt.started_at,
            "attempt_number": attempt.attempt_number,
            "questions": question_list,
            "time_limit": assessment.time_limit,
            "time_limit_seconds": assessment.time_limit * 60 if assessment.time_limit else None,
        }

    async def submit_attempt(
        self, attempt_id: str, user_id: str, responses_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        attempt = await self.attempt_repo.get(attempt_id)
        if attempt is None:
            raise NotFoundException(message="Attempt not found")
        profile = await self._get_student_profile(user_id)
        if attempt.student_id != profile.id:
            raise ValidationException(message="This attempt does not belong to you")
        if attempt.completed_at is not None:
            raise ValidationException(message="Attempt already submitted")

        questions = await self.question_repo.find_by_assessment(attempt.assessment_id)
        question_map = {q.id: q for q in questions}

        total_marks = sum(q.marks for q in questions)
        earned_marks = 0.0
        response_records = []

        for resp_data in responses_data:
            question_id = resp_data.get("question_id", "")
            student_response = resp_data.get("response", "")
            time_taken = resp_data.get("time_taken_seconds")

            question = question_map.get(question_id)
            if question is None:
                continue

            is_correct, score, feedback = self._grade_question(
                question, student_response
            )

            response_records.append(
                AssessmentResponse(
                    attempt_id=attempt.id,
                    question_id=question_id,
                    response=student_response,
                    is_correct=is_correct,
                    score=score,
                    feedback=feedback,
                    time_taken_seconds=time_taken,
                )
            )
            earned_marks += score

        for rr in response_records:
            self.session.add(rr)

        percentage = round((earned_marks / total_marks * 100), 2) if total_marks > 0 else 0.0
        passed = percentage >= (attempt.assessment.passing_score * 100)

        now = datetime.now(timezone.utc)
        attempt.score = earned_marks
        attempt.percentage = percentage
        attempt.passed = passed
        attempt.completed_at = now

        await self.session.flush()

        # -- Integration hooks --
        await self._on_assessment_completed(attempt, user_id)

        return {
            "attempt_id": attempt.id,
            "assessment_id": attempt.assessment_id,
            "score": earned_marks,
            "percentage": percentage,
            "passed": passed,
            "total_marks": total_marks,
            "earned_marks": earned_marks,
            "completed_at": now,
        }

    async def get_attempt_result(
        self, attempt_id: str, user_id: str
    ) -> dict[str, Any]:
        attempt = await self.attempt_repo.get(attempt_id)
        if attempt is None:
            raise NotFoundException(message="Attempt not found")
        profile = await self._get_student_profile(user_id)
        if attempt.student_id != profile.id:
            raise ValidationException(message="This attempt does not belong to you")

        assessment = await self._get_assessment(attempt.assessment_id)
        questions = await self.question_repo.find_by_assessment(attempt.assessment_id)
        question_map = {q.id: q for q in questions}
        responses = await self.response_repo.find_by_attempt(attempt.id)

        total_marks = sum(q.marks for q in questions)
        details = []
        for r in responses:
            q = question_map.get(r.question_id)
            if q is None:
                continue
            details.append({
                "question_id": q.id,
                "prompt": q.prompt,
                "question_type": q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
                "marks": q.marks,
                "response": r.response,
                "correct_answer": q.correct_answer,
                "is_correct": r.is_correct,
                "score": r.score,
                "feedback": r.feedback,
                "explanation": q.explanation,
            })

        return {
            "attempt_id": attempt.id,
            "assessment_id": attempt.assessment_id,
            "assessment_title": assessment.title,
            "assessment_type": assessment.assessment_type.value if hasattr(assessment.assessment_type, "value") else str(assessment.assessment_type),
            "passing_score": assessment.passing_score,
            "score": attempt.score,
            "percentage": attempt.percentage,
            "passed": attempt.passed,
            "attempt_number": attempt.attempt_number,
            "started_at": attempt.started_at,
            "completed_at": attempt.completed_at,
            "total_marks": total_marks,
            "earned_marks": attempt.score,
            "responses": details,
        }

    async def get_attempt_history(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        profile = await self._get_student_profile(user_id)
        attempts, total = await self.attempt_repo.find_by_student(
            profile.id, offset=(page - 1) * per_page, limit=per_page
        )

        items = []
        for a in attempts:
            assessment = await self.assessment_repo.get(a.assessment_id)
            items.append({
                "attempt_id": a.id,
                "assessment_id": a.assessment_id,
                "assessment_title": assessment.title if assessment else "",
                "assessment_type": assessment.assessment_type.value if assessment and hasattr(assessment.assessment_type, "value") else str(a.assessment_id),
                "score": a.score,
                "percentage": a.percentage,
                "passed": a.passed,
                "attempt_number": a.attempt_number,
                "started_at": a.started_at,
                "completed_at": a.completed_at,
            })

        return items, total

    # ------------------------------------------------------------------
    # Question Bank
    # ------------------------------------------------------------------

    async def create_bank_question(self, **kwargs: Any) -> QuestionBank:
        try:
            QuestionType(kwargs.get("question_type", ""))
        except ValueError:
            raise ValidationException(message=f"Invalid question type: {kwargs.get('question_type')}")
        return await self.bank_repo.create(**kwargs)

    async def update_bank_question(self, question_id: str, **kwargs: Any) -> QuestionBank:
        question = await self.bank_repo.get(question_id)
        if question is None:
            raise NotFoundException(message="Question bank item not found")
        if kwargs.get("question_type"):
            try:
                QuestionType(kwargs["question_type"])
            except ValueError:
                raise ValidationException(message=f"Invalid question type: {kwargs['question_type']}")
        updated = await self.bank_repo.update(question_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Question bank item not found")
        return updated

    async def delete_bank_question(self, question_id: str) -> None:
        question = await self.bank_repo.get(question_id)
        if question is None:
            raise NotFoundException(message="Question bank item not found")
        await self.bank_repo.delete(question.id)

    async def get_bank_questions(self, course_id: str | None = None) -> list[QuestionBank]:
        if course_id:
            return await self.bank_repo.find_by_course(course_id)
        return await self.bank_repo.find()

    # ------------------------------------------------------------------
    # Auto-Grading
    # ------------------------------------------------------------------

    def _grade_question(
        self, question: AssessmentQuestion, response: str
    ) -> tuple[bool, float, str | None]:
        qtype = question.question_type
        correct = question.correct_answer.strip()
        answer = response.strip()

        if qtype == QuestionType.MCQ:
            is_correct = answer.lower() == correct.lower()
        elif qtype == QuestionType.TRUE_FALSE:
            is_correct = answer.lower() == correct.lower()
        elif qtype == QuestionType.MULTI_SELECT:
            is_correct = self._grade_multi_select(answer, correct)
        elif qtype == QuestionType.NUMERIC:
            is_correct = self._grade_numeric(answer, correct)
        elif qtype == QuestionType.SHORT_ANSWER:
            is_correct = self._grade_short_answer(answer, correct)
        elif qtype == QuestionType.FILL_BLANK:
            is_correct = self._grade_fill_blank(answer, correct)
        else:
            is_correct = answer.lower() == correct.lower()

        score = question.marks if is_correct else 0.0
        feedback = None
        if is_correct:
            feedback = "Correct"
        else:
            feedback = f"Incorrect. Expected: {correct[:200]}"

        return is_correct, score, feedback

    def _grade_multi_select(self, response: str, correct: str) -> bool:
        resp_set = set(r.strip().lower() for r in response.split(",") if r.strip())
        correct_set = set(c.strip().lower() for c in correct.split(",") if c.strip())
        return resp_set == correct_set

    def _grade_numeric(self, response: str, correct: str) -> bool:
        try:
            resp_val = float(response)
            correct_val = float(correct)
            tolerance = abs(correct_val * 0.01)
            return abs(resp_val - correct_val) <= max(tolerance, 0.01)
        except (ValueError, TypeError):
            return response.strip().lower() == correct.strip().lower()

    def _grade_short_answer(self, response: str, correct: str) -> bool:
        resp_norm = re.sub(r"[^\w\s]", "", response.lower()).strip()
        correct_norm = re.sub(r"[^\w\s]", "", correct.lower()).strip()
        return resp_norm == correct_norm

    def _grade_fill_blank(self, response: str, correct: str) -> bool:
        pattern = r"\s*;\s*"
        resp_parts = sorted(p.strip().lower() for p in re.split(pattern, response) if p.strip())
        correct_parts = sorted(p.strip().lower() for p in re.split(pattern, correct) if p.strip())
        return resp_parts == correct_parts

    # ------------------------------------------------------------------
    # Integration Hooks
    # ------------------------------------------------------------------

    async def _on_assessment_completed(
        self, attempt: AssessmentAttempt, user_id: str
    ) -> None:
        assessment = await self._get_assessment(attempt.assessment_id)
        profile = await self._get_student_profile(user_id)

        # 1. Update lesson progress if linked
        if assessment.lesson_id:
            try:
                await self.progress_service.update_lesson_progress(
                    lesson_id=assessment.lesson_id,
                    user_id=user_id,
                    status=LessonProgressStatus.COMPLETED,
                    completion_percentage=attempt.percentage,
                )
            except Exception:
                pass

        # 2. Update mastery for concepts covered by the assessment
        concept_ids = set()
        if assessment.lesson_id:
            stmt = _select(Concept).where(Concept.lesson_id == assessment.lesson_id)
            result = await self.session.execute(stmt)
            for c in result.unique().scalars().all():
                concept_ids.add(c.id)
        elif assessment.module_id:
            stmt = (
                _select(Concept)
                .join(Lesson, Concept.lesson_id == Lesson.id)
                .where(Lesson.module_id == assessment.module_id)
            )
            result = await self.session.execute(stmt)
            for c in result.unique().scalars().all():
                concept_ids.add(c.id)

        for cid in concept_ids:
            try:
                await self.mastery_service.recalculate_mastery(profile.id, cid)
            except Exception:
                pass

        # 3. Update pacing based on performance
        enrollments = await self.enrollment_repo.find_by_student(profile.id)
        for enrollment in enrollments:
            if enrollment.course_id == assessment.course_id:
                schedule = await self.schedule_repo.find_by_enrollment(enrollment.id)
                if schedule:
                    from app.common.types import PaceStatus
                    new_status = PaceStatus.ON_TRACK if attempt.passed else PaceStatus.BEHIND
                    if new_status != schedule.pace_status:
                        await self.schedule_repo.update(
                            schedule.id,
                            pace_status=new_status,
                            last_pacing_adjustment_at=datetime.now(timezone.utc),
                        )
                break
