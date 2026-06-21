from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.common.exceptions import ConflictException, NotFoundException, ValidationException
from app.common.types import ConceptContentType, LessonStatus, QuestionType
from app.curriculum.models import (
    Concept,
    ConceptContent,
    Course,
    Example,
    Exercise,
    LearningObjective,
    Lesson,
    Module,
)
from app.curriculum.service import CourseService


def _make_course(**overrides) -> Course:
    defaults = dict(
        id="course-1",
        code="CS101",
        title="Intro",
        description="Desc",
        total_duration_hours=40,
        default_deadline_days=90,
        is_published=False,
        created_by="user-1",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return Course(**defaults)


def _make_module(**overrides) -> Module:
    defaults = dict(
        id="mod-1",
        course_id="course-1",
        title="Module 1",
        description="Desc",
        order_index=1,
        estimated_duration_hours=10,
    )
    defaults.update(overrides)
    return Module(**defaults)


def _make_lesson(**overrides) -> Lesson:
    defaults = dict(
        id="lsn-1",
        module_id="mod-1",
        title="Lesson 1",
        content_url=None,
        order_index=1,
        estimated_duration_minutes=30,
        is_required=True,
        status=LessonStatus.DRAFT,
    )
    defaults.update(overrides)
    return Lesson(**defaults)


def _make_concept(**overrides) -> Concept:
    defaults = dict(
        id="con-1",
        lesson_id="lsn-1",
        title="Concept 1",
        description=None,
        order_index=1,
        estimated_duration_minutes=15,
    )
    defaults.update(overrides)
    return Concept(**defaults)


def _make_content(**overrides) -> ConceptContent:
    defaults = dict(
        id="ct-1",
        concept_id="con-1",
        content_type=ConceptContentType.EXPLANATION,
        content="Some text",
        order_index=0,
        version=1,
    )
    defaults.update(overrides)
    return ConceptContent(**defaults)


def _make_example(**overrides) -> Example:
    defaults = dict(
        id="ex-1",
        concept_id="con-1",
        content="Example content",
        explanation="Explanation",
        order_index=1,
        tags=["tag1"],
    )
    defaults.update(overrides)
    return Example(**defaults)


def _make_exercise(**overrides) -> Exercise:
    defaults = dict(
        id="exr-1",
        concept_id="con-1",
        question_type=QuestionType.MCQ,
        prompt="What is X?",
        options={"A": "1", "B": "2"},
        correct_answer="A",
        difficulty=0.5,
        order_index=1,
        tags=None,
    )
    defaults.update(overrides)
    return Exercise(**defaults)


def _make_objective(**overrides) -> LearningObjective:
    defaults = dict(
        id="obj-1",
        lesson_id="lsn-1",
        code="LO1",
        description="Understand X",
        success_criterion=None,
        order_index=1,
    )
    defaults.update(overrides)
    return LearningObjective(**defaults)


# ---------------------------------------------------------------------------
# CourseService — Course
# ---------------------------------------------------------------------------

class TestCourseServiceCourse:
    @pytest.mark.asyncio
    async def test_create_course_success(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.course_repo.get_by_code = AsyncMock(return_value=None)
        service.course_repo.create = AsyncMock(return_value=_make_course())

        course = await service.create_course(
            user_id="user-1",
            code="CS101",
            title="Intro",
            total_duration_hours=40,
            default_deadline_days=90,
        )
        assert course.code == "CS101"
        assert course.title == "Intro"

    @pytest.mark.asyncio
    async def test_create_course_duplicate_code(self) -> None:
        mock_session = MagicMock()
        service = CourseService(mock_session)
        service.course_repo.get_by_code = AsyncMock(return_value=_make_course())

        with pytest.raises(ConflictException) as exc:
            await service.create_course(
                user_id="user-1", code="CS101", title="Intro",
                total_duration_hours=40, default_deadline_days=90,
            )
        assert exc.value.code == "CODE_EXISTS"

    @pytest.mark.asyncio
    async def test_get_course_not_found(self) -> None:
        mock_session = MagicMock()
        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_course("nonexistent")

    @pytest.mark.asyncio
    async def test_update_course_success(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        course = _make_course()
        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=course)
        service.course_repo.update = AsyncMock(return_value=_make_course(title="Updated"))

        updated = await service.update_course("course-1", title="Updated")
        assert updated.title == "Updated"

    @pytest.mark.asyncio
    async def test_delete_course_not_found(self) -> None:
        mock_session = MagicMock()
        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=_make_course())

        with patch.object(service, "course_repo") as mock_repo:
            mock_repo.get = AsyncMock(return_value=_make_course())

            stmt_result = MagicMock()
            stmt_result.unique.return_value.scalars.return_value.all.return_value = []
            mock_session.execute = AsyncMock(return_value=stmt_result)
            mock_repo.delete = AsyncMock(return_value=False)

            with pytest.raises(NotFoundException):
                await service.delete_course("course-1")

    @pytest.mark.asyncio
    async def test_delete_course_with_active_enrollment(self) -> None:
        mock_session = MagicMock()
        service = CourseService(mock_session)

        active_enrollment = MagicMock()
        active_enrollment.id = "enr-1"

        stmt_result = MagicMock()
        stmt_result.unique.return_value.scalars.return_value.all.return_value = [active_enrollment]
        mock_session.execute = AsyncMock(return_value=stmt_result)

        with pytest.raises(ConflictException) as exc:
            await service.delete_course("course-1")
        assert exc.value.code == "HAS_ACTIVE_ENROLLMENTS"

    @pytest.mark.asyncio
    async def test_publish_course_success(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        course = _make_course()
        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=course)
        service.module_repo.find_by_course = AsyncMock(return_value=[_make_module()])
        service.lesson_repo.find_by_module = AsyncMock(return_value=[_make_lesson()])

        published = await service.publish_course("course-1", True)
        assert published.is_published is True

    @pytest.mark.asyncio
    async def test_publish_course_no_modules(self) -> None:
        mock_session = MagicMock()
        course = _make_course()
        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=course)
        service.module_repo.find_by_course = AsyncMock(return_value=[])

        with pytest.raises(ValidationException):
            await service.publish_course("course-1", True)

    @pytest.mark.asyncio
    async def test_publish_course_module_no_lessons(self) -> None:
        mock_session = MagicMock()
        course = _make_course()
        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=course)
        service.module_repo.find_by_course = AsyncMock(return_value=[_make_module()])
        service.lesson_repo.find_by_module = AsyncMock(return_value=[])

        with pytest.raises(ValidationException):
            await service.publish_course("course-1", True)

    @pytest.mark.asyncio
    async def test_list_courses(self) -> None:
        mock_session = MagicMock()
        service = CourseService(mock_session)
        service.course_repo.find_paginated = AsyncMock(return_value=([_make_course()], 1))

        courses, total = await service.list_courses(page=1, per_page=20)
        assert len(courses) == 1
        assert total == 1


# ---------------------------------------------------------------------------
# CourseService — Module
# ---------------------------------------------------------------------------

class TestCourseServiceModule:
    @pytest.mark.asyncio
    async def test_create_module(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=_make_course())
        service.module_repo.get_max_order = AsyncMock(return_value=0)
        service.module_repo.create = AsyncMock(return_value=_make_module())

        module = await service.create_module("course-1", title="M1", order_index=1)
        assert module.title == "Module 1"

    @pytest.mark.asyncio
    async def test_create_module_auto_order(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.course_repo.get = AsyncMock(return_value=_make_course())
        service.module_repo.get_max_order = AsyncMock(return_value=2)

        async def fake_create(**kwargs):
            kwargs.setdefault("order_index", 3)
            return _make_module(order_index=kwargs["order_index"])

        service.module_repo.create = AsyncMock(side_effect=fake_create)

        module = await service.create_module("course-1", title="M2", order_index=999)
        assert module.order_index == 3

    @pytest.mark.asyncio
    async def test_delete_module_not_found(self) -> None:
        mock_session = MagicMock()
        service = CourseService(mock_session)
        service.module_repo.delete = AsyncMock(return_value=False)

        with pytest.raises(NotFoundException):
            await service.delete_module("nonexistent")


# ---------------------------------------------------------------------------
# CourseService — Lesson
# ---------------------------------------------------------------------------

class TestCourseServiceLesson:
    @pytest.mark.asyncio
    async def test_create_lesson(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.module_repo.get = AsyncMock(return_value=_make_module())
        service.lesson_repo.get_max_order = AsyncMock(return_value=0)
        service.lesson_repo.create = AsyncMock(return_value=_make_lesson())

        lesson = await service.create_lesson("mod-1", title="L1", order_index=1)
        assert lesson.title == "Lesson 1"


# ---------------------------------------------------------------------------
# CourseService — Concept
# ---------------------------------------------------------------------------

class TestCourseServiceConcept:
    @pytest.mark.asyncio
    async def test_create_concept(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.lesson_repo.get = AsyncMock(return_value=_make_lesson())
        service.concept_repo.get_max_order = AsyncMock(return_value=0)
        service.concept_repo.create = AsyncMock(return_value=_make_concept())

        concept = await service.create_concept("lsn-1", title="C1", order_index=1)
        assert concept.title == "Concept 1"


# ---------------------------------------------------------------------------
# CourseService — ConceptContent
# ---------------------------------------------------------------------------

class TestCourseServiceContent:
    @pytest.mark.asyncio
    async def test_create_content(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.concept_repo.get = AsyncMock(return_value=_make_concept())
        service.content_repo.get_max_order = AsyncMock(return_value=0)
        service.content_repo.create = AsyncMock(return_value=_make_content())

        content = await service.create_content(
            "con-1", content_type=ConceptContentType.EXPLANATION, content="Hello", order_index=0
        )
        assert content.content == "Some text"

    @pytest.mark.asyncio
    async def test_update_content_bumps_version(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        existing = _make_content(version=1)
        service = CourseService(mock_session)
        service.content_repo.get = AsyncMock(return_value=existing)
        service.content_repo.update = AsyncMock(return_value=_make_content(version=2))

        updated = await service.update_content("ct-1", content="Updated text")
        assert updated.version == 2


# ---------------------------------------------------------------------------
# CourseService — Example
# ---------------------------------------------------------------------------

class TestCourseServiceExample:
    @pytest.mark.asyncio
    async def test_create_example(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.concept_repo.get = AsyncMock(return_value=_make_concept())
        service.example_repo.get_max_order = AsyncMock(return_value=0)
        service.example_repo.create = AsyncMock(return_value=_make_example())

        example = await service.create_example("con-1", content="Ex", order_index=1)
        assert example.content == "Example content"


# ---------------------------------------------------------------------------
# CourseService — Exercise
# ---------------------------------------------------------------------------

class TestCourseServiceExercise:
    @pytest.mark.asyncio
    async def test_create_exercise(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.concept_repo.get = AsyncMock(return_value=_make_concept())
        service.exercise_repo.get_max_order = AsyncMock(return_value=0)
        service.exercise_repo.create = AsyncMock(return_value=_make_exercise())

        exercise = await service.create_exercise(
            "con-1", question_type=QuestionType.MCQ,
            prompt="Q?", correct_answer="A", order_index=1,
        )
        assert exercise.prompt == "What is X?"


# ---------------------------------------------------------------------------
# CourseService — LearningObjective
# ---------------------------------------------------------------------------

class TestCourseServiceObjective:
    @pytest.mark.asyncio
    async def test_create_objective(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        service = CourseService(mock_session)
        service.lesson_repo.get = AsyncMock(return_value=_make_lesson())
        service.objective_repo.get_max_order = AsyncMock(return_value=0)
        service.objective_repo.create = AsyncMock(return_value=_make_objective())

        obj = await service.create_objective("lsn-1", code="LO1", description="X", order_index=1)
        assert obj.code == "LO1"

    @pytest.mark.asyncio
    async def test_delete_objective_not_found(self) -> None:
        mock_session = MagicMock()
        service = CourseService(mock_session)
        service.objective_repo.delete = AsyncMock(return_value=False)

        with pytest.raises(NotFoundException):
            await service.delete_objective("nonexistent")
