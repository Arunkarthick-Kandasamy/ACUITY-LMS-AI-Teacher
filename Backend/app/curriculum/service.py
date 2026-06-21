from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, NotFoundException, ValidationException
from app.curriculum.models import Concept, ConceptContent, Course, Example, Exercise, LearningObjective, Lesson, Module
from app.curriculum.repository import (
    ConceptContentRepository,
    ConceptRepository,
    CourseRepository,
    ExampleRepository,
    ExerciseRepository,
    LearningObjectiveRepository,
    LessonRepository,
    ModuleRepository,
)


class CourseService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.course_repo = CourseRepository(session)
        self.module_repo = ModuleRepository(session)
        self.lesson_repo = LessonRepository(session)
        self.concept_repo = ConceptRepository(session)
        self.content_repo = ConceptContentRepository(session)
        self.example_repo = ExampleRepository(session)
        self.exercise_repo = ExerciseRepository(session)
        self.objective_repo = LearningObjectiveRepository(session)

    async def create_course(self, user_id: str, **kwargs) -> Course:
        existing = await self.course_repo.get_by_code(kwargs["code"])
        if existing is not None:
            raise ConflictException(message=f"Course code '{kwargs['code']}' already exists", code="CODE_EXISTS")
        return await self.course_repo.create(created_by=user_id, **kwargs)

    async def get_course(self, course_id: str) -> Course:
        course = await self.course_repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")
        return course

    async def update_course(self, course_id: str, **kwargs) -> Course:
        existing = await self.course_repo.get(course_id)
        if existing is None:
            raise NotFoundException(message="Course not found")
        if "code" in kwargs and kwargs["code"] != existing.code:
            dup = await self.course_repo.get_by_code(kwargs["code"])
            if dup is not None:
                raise ConflictException(message=f"Course code '{kwargs['code']}' already exists", code="CODE_EXISTS")
        updated = await self.course_repo.update(course_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Course not found")
        return updated

    async def delete_course(self, course_id: str) -> None:
        from app.enrollment.models import StudentCourseEnrollment

        stmt = select(StudentCourseEnrollment).where(
            StudentCourseEnrollment.course_id == course_id,
            StudentCourseEnrollment.status.in_(["active", "paused"]),
        )
        result = await self.session.execute(stmt)
        active = result.unique().scalars().all()
        if active:
            raise ConflictException(
                message=f"Cannot delete course with {len(active)} active enrollments. Cancel enrollments first.",
                code="HAS_ACTIVE_ENROLLMENTS",
            )
        deleted = await self.course_repo.delete(course_id)
        if not deleted:
            raise NotFoundException(message="Course not found")

    async def list_courses(
        self, is_published: bool | None = None, search: str | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[Course], int]:
        offset = (page - 1) * per_page
        return await self.course_repo.find_paginated(
            is_published=is_published, search=search, offset=offset, limit=per_page
        )

    async def publish_course(self, course_id: str, is_published: bool) -> Course:
        course = await self.course_repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")
        if is_published:
            modules = await self.module_repo.find_by_course(course_id)
            if not modules:
                raise ValidationException(message="Course must have at least one module to publish")
            for mod in modules:
                lessons = await self.lesson_repo.find_by_module(mod.id)
                if not lessons:
                    raise ValidationException(
                        message=f"Module '{mod.title}' must have at least one lesson before publishing"
                    )
        course.is_published = is_published
        await self.session.flush()
        await self.session.refresh(course)
        return course

    async def get_course_detail(self, course_id: str) -> Course:
        course = await self.course_repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")
        return course

    async def get_lesson_detail(self, lesson_id: str) -> Lesson:
        lesson = await self.lesson_repo.get(lesson_id)
        if lesson is None:
            raise NotFoundException(message="Lesson not found")
        return lesson

    async def get_concept_detail(self, concept_id: str) -> Concept:
        concept = await self.concept_repo.get(concept_id)
        if concept is None:
            raise NotFoundException(message="Concept not found")
        return concept

    # -----------------------------------------------------------------------
    # Module
    # -----------------------------------------------------------------------

    async def create_module(self, course_id: str, **kwargs) -> Module:
        course = await self.course_repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")
        max_order = await self.module_repo.get_max_order(course_id)
        if "order_index" not in kwargs or kwargs["order_index"] > max_order + 1:
            kwargs["order_index"] = max_order + 1
        return await self.module_repo.create(course_id=course_id, **kwargs)

    async def get_module(self, module_id: str) -> Module:
        module = await self.module_repo.get(module_id)
        if module is None:
            raise NotFoundException(message="Module not found")
        return module

    async def update_module(self, module_id: str, **kwargs) -> Module:
        existing = await self.module_repo.get(module_id)
        if existing is None:
            raise NotFoundException(message="Module not found")
        updated = await self.module_repo.update(module_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Module not found")
        return updated

    async def delete_module(self, module_id: str) -> None:
        deleted = await self.module_repo.delete(module_id)
        if not deleted:
            raise NotFoundException(message="Module not found")

    async def list_modules(self, course_id: str) -> list[Module]:
        return await self.module_repo.find_by_course(course_id)

    # -----------------------------------------------------------------------
    # Lesson
    # -----------------------------------------------------------------------

    async def create_lesson(self, module_id: str, **kwargs) -> Lesson:
        module = await self.module_repo.get(module_id)
        if module is None:
            raise NotFoundException(message="Module not found")
        max_order = await self.lesson_repo.get_max_order(module_id)
        if "order_index" not in kwargs or kwargs["order_index"] > max_order + 1:
            kwargs["order_index"] = max_order + 1
        return await self.lesson_repo.create(module_id=module_id, **kwargs)

    async def get_lesson(self, lesson_id: str) -> Lesson:
        lesson = await self.lesson_repo.get(lesson_id)
        if lesson is None:
            raise NotFoundException(message="Lesson not found")
        return lesson

    async def update_lesson(self, lesson_id: str, **kwargs) -> Lesson:
        existing = await self.lesson_repo.get(lesson_id)
        if existing is None:
            raise NotFoundException(message="Lesson not found")
        updated = await self.lesson_repo.update(lesson_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Lesson not found")
        return updated

    async def delete_lesson(self, lesson_id: str) -> None:
        deleted = await self.lesson_repo.delete(lesson_id)
        if not deleted:
            raise NotFoundException(message="Lesson not found")

    async def list_lessons(self, module_id: str) -> list[Lesson]:
        return await self.lesson_repo.find_by_module(module_id)

    # -----------------------------------------------------------------------
    # Concept
    # -----------------------------------------------------------------------

    async def create_concept(self, lesson_id: str, **kwargs) -> Concept:
        lesson = await self.lesson_repo.get(lesson_id)
        if lesson is None:
            raise NotFoundException(message="Lesson not found")
        max_order = await self.concept_repo.get_max_order(lesson_id)
        if "order_index" not in kwargs or kwargs["order_index"] > max_order + 1:
            kwargs["order_index"] = max_order + 1
        return await self.concept_repo.create(lesson_id=lesson_id, **kwargs)

    async def get_concept(self, concept_id: str) -> Concept:
        concept = await self.concept_repo.get(concept_id)
        if concept is None:
            raise NotFoundException(message="Concept not found")
        return concept

    async def update_concept(self, concept_id: str, **kwargs) -> Concept:
        existing = await self.concept_repo.get(concept_id)
        if existing is None:
            raise NotFoundException(message="Concept not found")
        updated = await self.concept_repo.update(concept_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Concept not found")
        return updated

    async def delete_concept(self, concept_id: str) -> None:
        deleted = await self.concept_repo.delete(concept_id)
        if not deleted:
            raise NotFoundException(message="Concept not found")

    async def list_concepts(self, lesson_id: str) -> list[Concept]:
        return await self.concept_repo.find_by_lesson(lesson_id)

    # -----------------------------------------------------------------------
    # ConceptContent
    # -----------------------------------------------------------------------

    async def create_content(self, concept_id: str, **kwargs) -> ConceptContent:
        concept = await self.concept_repo.get(concept_id)
        if concept is None:
            raise NotFoundException(message="Concept not found")
        max_order = await self.content_repo.get_max_order(concept_id)
        if "order_index" not in kwargs or kwargs["order_index"] > max_order + 1:
            kwargs["order_index"] = max_order + 1
        return await self.content_repo.create(concept_id=concept_id, **kwargs)

    async def update_content(self, content_id: str, **kwargs) -> ConceptContent:
        existing = await self.content_repo.get(content_id)
        if existing is None:
            raise NotFoundException(message="Content not found")
        kwargs["version"] = existing.version + 1
        updated = await self.content_repo.update(content_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Content not found")
        return updated

    async def delete_content(self, content_id: str) -> None:
        deleted = await self.content_repo.delete(content_id)
        if not deleted:
            raise NotFoundException(message="Content not found")

    async def list_contents(self, concept_id: str) -> list[ConceptContent]:
        return await self.content_repo.find_by_concept(concept_id)

    # -----------------------------------------------------------------------
    # Example
    # -----------------------------------------------------------------------

    async def create_example(self, concept_id: str, **kwargs) -> Example:
        concept = await self.concept_repo.get(concept_id)
        if concept is None:
            raise NotFoundException(message="Concept not found")
        max_order = await self.example_repo.get_max_order(concept_id)
        if "order_index" not in kwargs or kwargs["order_index"] > max_order + 1:
            kwargs["order_index"] = max_order + 1
        return await self.example_repo.create(concept_id=concept_id, **kwargs)

    async def list_examples(self, concept_id: str) -> list[Example]:
        return await self.example_repo.find_by_concept(concept_id)

    async def update_example(self, example_id: str, **kwargs) -> Example:
        existing = await self.example_repo.get(example_id)
        if existing is None:
            raise NotFoundException(message="Example not found")
        updated = await self.example_repo.update(example_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Example not found")
        return updated

    async def delete_example(self, example_id: str) -> None:
        deleted = await self.example_repo.delete(example_id)
        if not deleted:
            raise NotFoundException(message="Example not found")

    # -----------------------------------------------------------------------
    # Exercise
    # -----------------------------------------------------------------------

    async def create_exercise(self, concept_id: str, **kwargs) -> Exercise:
        concept = await self.concept_repo.get(concept_id)
        if concept is None:
            raise NotFoundException(message="Concept not found")
        max_order = await self.exercise_repo.get_max_order(concept_id)
        if "order_index" not in kwargs or kwargs["order_index"] > max_order + 1:
            kwargs["order_index"] = max_order + 1
        return await self.exercise_repo.create(concept_id=concept_id, **kwargs)

    async def update_exercise(self, exercise_id: str, **kwargs) -> Exercise:
        existing = await self.exercise_repo.get(exercise_id)
        if existing is None:
            raise NotFoundException(message="Exercise not found")
        updated = await self.exercise_repo.update(exercise_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Exercise not found")
        return updated

    async def delete_exercise(self, exercise_id: str) -> None:
        deleted = await self.exercise_repo.delete(exercise_id)
        if not deleted:
            raise NotFoundException(message="Exercise not found")

    async def list_exercises(self, concept_id: str) -> list[Exercise]:
        return await self.exercise_repo.find_by_concept(concept_id)

    # -----------------------------------------------------------------------
    # LearningObjective
    # -----------------------------------------------------------------------

    async def create_objective(self, lesson_id: str, **kwargs) -> LearningObjective:
        lesson = await self.lesson_repo.get(lesson_id)
        if lesson is None:
            raise NotFoundException(message="Lesson not found")
        max_order = await self.objective_repo.get_max_order(lesson_id)
        if "order_index" not in kwargs or kwargs["order_index"] > max_order + 1:
            kwargs["order_index"] = max_order + 1
        return await self.objective_repo.create(lesson_id=lesson_id, **kwargs)

    async def update_objective(self, objective_id: str, **kwargs) -> LearningObjective:
        existing = await self.objective_repo.get(objective_id)
        if existing is None:
            raise NotFoundException(message="Learning objective not found")
        updated = await self.objective_repo.update(objective_id, **kwargs)
        if updated is None:
            raise NotFoundException(message="Learning objective not found")
        return updated

    async def list_objectives(self, lesson_id: str) -> list[LearningObjective]:
        lesson = await self.lesson_repo.get(lesson_id)
        if lesson is None:
            raise NotFoundException(message="Lesson not found")
        return await self.objective_repo.find_by_lesson(lesson_id)

    async def delete_objective(self, objective_id: str) -> None:
        deleted = await self.objective_repo.delete(objective_id)
        if not deleted:
            raise NotFoundException(message="Learning objective not found")
