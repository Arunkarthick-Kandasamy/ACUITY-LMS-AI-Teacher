from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.exceptions import ForbiddenException
from app.common.response import paginated_response, success_response
from app.common.types import UserRole
from app.config import settings
from app.curriculum.schemas import (
    CatalogCourseResponse,
    ConceptContentCreate,
    ConceptContentResponse,
    ConceptCreate,
    ConceptDetailResponse,
    ConceptListResponse,
    ConceptResponse,
    ConceptUpdate,
    ContentBrief,
    CourseCreate,
    CourseDetailResponse,
    CourseListResponse,
    CoursePublishRequest,
    CoursePublishResponse,
    CourseResponse,
    CourseUpdate,
    DeleteMessage,
    ExampleBrief,
    ExampleCreate,
    ExampleResponse,
    ExampleUpdate,
    ExerciseCreate,
    ExerciseListResponse,
    ExerciseResponse,
    ExerciseUpdate,
    LearningObjectiveCreate,
    LearningObjectiveResponse,
    LearningObjectiveUpdate,
    LessonBrief,
    LessonCreate,
    LessonDetailResponse,
    LessonListResponse,
    LessonResponse,
    LessonUpdate,
    ModuleCreate,
    ModuleDetail,
    ModuleListResponse,
    ModuleResponse,
    ModuleUpdate,
)
from app.curriculum.service import CourseService
from app.infrastructure.database import get_session
from app.teacher.repository import TeacherCourseAssignmentRepository
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["Curriculum"])

admin_only = require_roles(UserRole.ADMIN)
course_admin_or_admin = require_roles(UserRole.COURSE_ADMIN, UserRole.ADMIN)


async def _verify_course_access(
    course_id: str,
    current_user: User,
    session: AsyncSession,
) -> None:
    if current_user.role == UserRole.ADMIN:
        return
    repo = TeacherCourseAssignmentRepository(session)
    assignment = await repo.find_by_teacher_and_course(current_user.id, course_id)
    if assignment is None:
        raise ForbiddenException(message="You are not assigned to this course")


async def _resolve_and_verify_access(
    session: AsyncSession,
    current_user: User,
    entity_type: str,
    entity_id: str,
) -> None:
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role != UserRole.COURSE_ADMIN:
        raise ForbiddenException(message="Access denied")

    course_id = None
    if entity_type == "module":
        from app.curriculum.repository import ModuleRepository
        module = await ModuleRepository(session).get(entity_id)
        if module:
            course_id = module.course_id
    elif entity_type == "lesson":
        from app.curriculum.repository import LessonRepository, ModuleRepository as ModRepo
        lesson = await LessonRepository(session).get(entity_id)
        if lesson:
            module = await ModRepo(session).get(lesson.module_id)
            if module:
                course_id = module.course_id
    elif entity_type == "concept":
        from app.curriculum.repository import ConceptRepository, LessonRepository as LesRepo, ModuleRepository as ModRepo2
        concept = await ConceptRepository(session).get(entity_id)
        if concept:
            lesson = await LesRepo(session).get(concept.lesson_id)
            if lesson:
                module = await ModRepo2(session).get(lesson.module_id)
                if module:
                    course_id = module.course_id
    elif entity_type in ("content", "exercise", "example"):
        from app.curriculum.repository import (
            ConceptContentRepository, ExerciseRepository, ExampleRepository,
            ConceptRepository as ConRepo, LessonRepository as LesRepo2, ModuleRepository as ModRepo3,
        )
        repo_map = {
            "content": ConceptContentRepository(session),
            "exercise": ExerciseRepository(session),
            "example": ExampleRepository(session),
        }
        entity = await repo_map[entity_type].get(entity_id)
        if entity:
            concept = await ConRepo(session).get(entity.concept_id)
            if concept:
                lesson = await LesRepo2(session).get(concept.lesson_id)
                if lesson:
                    module = await ModRepo3(session).get(lesson.module_id)
                    if module:
                        course_id = module.course_id
    elif entity_type == "objective":
        from app.curriculum.repository import LearningObjectiveRepository as ObjRepo, LessonRepository as LesRepo3, ModuleRepository as ModRepo4
        obj = await ObjRepo(session).get(entity_id)
        if obj:
            lesson = await LesRepo3(session).get(obj.lesson_id)
            if lesson:
                module = await ModRepo4(session).get(lesson.module_id)
                if module:
                    course_id = module.course_id

    if course_id:
        await _verify_course_access(course_id, current_user, session)


# -----------------------------------------------------------------------
# Public Catalog
# -----------------------------------------------------------------------

@router.get("/catalog")
async def get_catalog(
    search: str | None = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = CourseService(session)
    courses, total = await service.list_courses(
        is_published=True, search=search, page=page, per_page=per_page
    )
    items = []
    for c in courses:
        teacher_name = c.created_by_user.full_name if c.created_by_user else None
        module_count = len(c.modules) if hasattr(c, "modules") else 0
        lesson_count = sum(len(m.lessons) for m in c.modules) if hasattr(c, "modules") else 0
        items.append(
            CatalogCourseResponse(
                course_id=c.id,
                code=c.code,
                title=c.title,
                description=c.description,
                teacher_name=teacher_name,
                total_duration_hours=c.total_duration_hours,
                default_deadline_days=c.default_deadline_days,
                module_count=module_count,
                lesson_count=lesson_count,
                created_at=c.created_at,
            ).model_dump(mode="json")
        )
    return paginated_response(items, total, page, per_page)


# -----------------------------------------------------------------------
# Courses
# -----------------------------------------------------------------------

@router.post("/courses", status_code=201)
async def create_course(
    body: CourseCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    service = CourseService(session)
    course = await service.create_course(user_id=current_user.id, **body.model_dump())
    return success_response(CourseResponse.model_validate(course).model_dump(mode="json"))


@router.get("/courses")
async def list_courses(
    is_published: bool | None = Query(None),
    search: str | None = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    courses, total = await service.list_courses(
        is_published=is_published, search=search, page=page, per_page=per_page
    )
    items = []
    for c in courses:
        module_count = len(c.modules) if hasattr(c, "modules") else 0
        lesson_count = sum(len(m.lessons) for m in c.modules) if hasattr(c, "modules") else 0
        items.append(
            CourseListResponse(
                course_id=c.id,
                code=c.code,
                title=c.title,
                description=c.description,
                total_duration_hours=c.total_duration_hours,
                default_deadline_days=c.default_deadline_days,
                is_published=c.is_published,
                module_count=module_count,
                lesson_count=lesson_count,
                created_at=c.created_at,
            ).model_dump(mode="json")
        )
    return paginated_response(items, total, page, per_page)


@router.get("/courses/{course_id}")
async def get_course(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    course = await service.get_course_detail(course_id)
    modules = []
    for m in course.modules:
        lessons = []
        for lsn in m.lessons:
            lessons.append(
                LessonBrief(
                    lesson_id=lsn.id,
                    title=lsn.title,
                    order_index=lsn.order_index,
                    estimated_duration_minutes=lsn.estimated_duration_minutes,
                    concept_count=len(lsn.concepts) if hasattr(lsn, "concepts") else 0,
                ).model_dump(mode="json")
            )
        modules.append(
            ModuleDetail(
                module_id=m.id,
                title=m.title,
                order_index=m.order_index,
                lessons=lessons,
            ).model_dump(mode="json")
        )
    return success_response(
        CourseDetailResponse(
            course_id=course.id,
            code=course.code,
            title=course.title,
            description=course.description,
            total_duration_hours=course.total_duration_hours,
            default_deadline_days=course.default_deadline_days,
            is_published=course.is_published,
            modules=modules,
            created_at=course.created_at,
        ).model_dump(mode="json")
    )


@router.put("/courses/{course_id}")
async def update_course(
    course_id: str,
    body: CourseUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _verify_course_access(course_id, current_user, session)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    course = await service.update_course(course_id, **kwargs)
    return success_response(CourseResponse.model_validate(course).model_dump(mode="json"))


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _verify_course_access(course_id, current_user, session)
    service = CourseService(session)
    await service.delete_course(course_id)
    return success_response(DeleteMessage(message="Course deleted successfully").model_dump())


@router.put("/courses/{course_id}/publish")
async def publish_course(
    course_id: str,
    body: CoursePublishRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _verify_course_access(course_id, current_user, session)
    service = CourseService(session)
    course = await service.publish_course(course_id, body.is_published)
    return success_response(
        CoursePublishResponse(
            course_id=course.id,
            is_published=course.is_published,
            updated_at=course.updated_at,
        ).model_dump(mode="json")
    )


# -----------------------------------------------------------------------
# Modules
# -----------------------------------------------------------------------

@router.post("/courses/{course_id}/modules", status_code=201)
async def create_module(
    course_id: str,
    body: ModuleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _verify_course_access(course_id, current_user, session)
    service = CourseService(session)
    module = await service.create_module(course_id, **body.model_dump())
    return success_response(ModuleResponse.model_validate(module).model_dump(mode="json"))


@router.get("/courses/{course_id}/modules")
async def list_modules(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    modules = await service.list_modules(course_id)
    items = []
    for m in modules:
        lesson_count = len(m.lessons) if hasattr(m, "lessons") else 0
        items.append(
            ModuleListResponse(
                module_id=m.id,
                title=m.title,
                description=m.description,
                order_index=m.order_index,
                estimated_duration_hours=m.estimated_duration_hours,
                lesson_count=lesson_count,
            ).model_dump(mode="json")
        )
    return success_response(items)


@router.put("/modules/{module_id}")
async def update_module(
    module_id: str,
    body: ModuleUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "module", module_id)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    module = await service.update_module(module_id, **kwargs)
    return success_response(ModuleResponse.model_validate(module).model_dump(mode="json"))


@router.delete("/modules/{module_id}")
async def delete_module(
    module_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "module", module_id)
    service = CourseService(session)
    await service.delete_module(module_id)
    return success_response(DeleteMessage(message="Module deleted successfully").model_dump())


# -----------------------------------------------------------------------
# Lessons
# -----------------------------------------------------------------------

@router.post("/modules/{module_id}/lessons", status_code=201)
async def create_lesson(
    module_id: str,
    body: LessonCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "module", module_id)
    service = CourseService(session)
    lesson = await service.create_lesson(module_id, **body.model_dump())
    return success_response(LessonResponse.model_validate(lesson).model_dump(mode="json"))


@router.get("/modules/{module_id}/lessons")
async def list_lessons(
    module_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    lessons = await service.list_lessons(module_id)
    items = []
    for lsn in lessons:
        concept_count = len(lsn.concepts) if hasattr(lsn, "concepts") else 0
        items.append(
            LessonListResponse(
                lesson_id=lsn.id,
                title=lsn.title,
                order_index=lsn.order_index,
                estimated_duration_minutes=lsn.estimated_duration_minutes,
                status=lsn.status,
                concept_count=concept_count,
            ).model_dump(mode="json")
        )
    return success_response(items)


@router.get("/lessons/{lesson_id}")
async def get_lesson(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    lesson = await service.get_lesson_detail(lesson_id)
    concepts = [
        ConceptListResponse(
            concept_id=c.id,
            title=c.title,
            description=c.description,
            order_index=c.order_index,
            estimated_duration_minutes=c.estimated_duration_minutes,
            content_count=len(c.contents) if hasattr(c, "contents") else 0,
            exercise_count=len(c.exercises) if hasattr(c, "exercises") else 0,
        ).model_dump(mode="json")
        for c in (lesson.concepts if hasattr(lesson, "concepts") else [])
    ]
    return success_response(
        LessonDetailResponse(
            lesson_id=lesson.id,
            module_id=lesson.module_id,
            title=lesson.title,
            content_url=lesson.content_url,
            order_index=lesson.order_index,
            estimated_duration_minutes=lesson.estimated_duration_minutes,
            status=lesson.status,
            concepts=concepts,
        ).model_dump(mode="json")
    )


@router.put("/lessons/{lesson_id}")
async def update_lesson(
    lesson_id: str,
    body: LessonUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "lesson", lesson_id)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    lesson = await service.update_lesson(lesson_id, **kwargs)
    return success_response(LessonResponse.model_validate(lesson).model_dump(mode="json"))


@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "lesson", lesson_id)
    service = CourseService(session)
    await service.delete_lesson(lesson_id)
    return success_response(DeleteMessage(message="Lesson deleted successfully").model_dump())


# -----------------------------------------------------------------------
# Concepts
# -----------------------------------------------------------------------

@router.post("/lessons/{lesson_id}/concepts", status_code=201)
async def create_concept(
    lesson_id: str,
    body: ConceptCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "lesson", lesson_id)
    service = CourseService(session)
    concept = await service.create_concept(lesson_id, **body.model_dump())
    return success_response(ConceptResponse.model_validate(concept).model_dump(mode="json"))


@router.get("/lessons/{lesson_id}/concepts")
async def list_concepts(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    concepts = await service.list_concepts(lesson_id)
    items = []
    for c in concepts:
        items.append(
            ConceptListResponse(
                concept_id=c.id,
                title=c.title,
                description=c.description,
                order_index=c.order_index,
                estimated_duration_minutes=c.estimated_duration_minutes,
                content_count=len(c.contents) if hasattr(c, "contents") else 0,
                exercise_count=len(c.exercises) if hasattr(c, "exercises") else 0,
            ).model_dump(mode="json")
        )
    return success_response(items)


@router.get("/concepts/{concept_id}")
async def get_concept(
    concept_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    concept = await service.get_concept_detail(concept_id)
    contents = [
        ContentBrief(
            content_id=co.id,
            content_type=co.content_type,
            content=co.content,
            order_index=co.order_index,
        ).model_dump(mode="json")
        for co in (concept.contents if hasattr(concept, "contents") else [])
    ]
    examples = [
        ExampleBrief(
            example_id=e.id,
            content=e.content,
            explanation=e.explanation,
        ).model_dump(mode="json")
        for e in (concept.examples if hasattr(concept, "examples") else [])
    ]
    exercise_count = len(concept.exercises) if hasattr(concept, "exercises") else 0
    return success_response(
        ConceptDetailResponse(
            concept_id=concept.id,
            lesson_id=concept.lesson_id,
            title=concept.title,
            description=concept.description,
            order_index=concept.order_index,
            estimated_duration_minutes=concept.estimated_duration_minutes,
            contents=contents,
            examples=examples,
            exercise_count=exercise_count,
        ).model_dump(mode="json")
    )


@router.put("/concepts/{concept_id}")
async def update_concept(
    concept_id: str,
    body: ConceptUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "concept", concept_id)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    concept = await service.update_concept(concept_id, **kwargs)
    return success_response(ConceptResponse.model_validate(concept).model_dump(mode="json"))


@router.delete("/concepts/{concept_id}")
async def delete_concept(
    concept_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "concept", concept_id)
    service = CourseService(session)
    await service.delete_concept(concept_id)
    return success_response(DeleteMessage(message="Concept deleted successfully").model_dump())


# -----------------------------------------------------------------------
# ConceptContents
# -----------------------------------------------------------------------

@router.post("/concepts/{concept_id}/contents", status_code=201)
async def create_content(
    concept_id: str,
    body: ConceptContentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "concept", concept_id)
    service = CourseService(session)
    content = await service.create_content(concept_id, **body.model_dump())
    return success_response(ConceptContentResponse.model_validate(content).model_dump(mode="json"))


@router.get("/concepts/{concept_id}/contents")
async def list_contents(
    concept_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    contents = await service.list_contents(concept_id)
    items = [
        ConceptContentResponse.model_validate(c).model_dump(mode="json") for c in contents
    ]
    return success_response(items)


@router.put("/concept-contents/{content_id}")
async def update_content(
    content_id: str,
    body: ConceptContentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "content", content_id)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    content = await service.update_content(content_id, **kwargs)
    return success_response(ConceptContentResponse.model_validate(content).model_dump(mode="json"))


@router.delete("/concept-contents/{content_id}")
async def delete_content(
    content_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "content", content_id)
    service = CourseService(session)
    await service.delete_content(content_id)
    return success_response(DeleteMessage(message="Content deleted successfully").model_dump())


# -----------------------------------------------------------------------
# Exercises
# -----------------------------------------------------------------------

@router.post("/concepts/{concept_id}/exercises", status_code=201)
async def create_exercise(
    concept_id: str,
    body: ExerciseCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "concept", concept_id)
    service = CourseService(session)
    exercise = await service.create_exercise(concept_id, **body.model_dump())
    return success_response(ExerciseResponse.model_validate(exercise).model_dump(mode="json"))


@router.get("/concepts/{concept_id}/exercises")
async def list_exercises(
    concept_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    exercises = await service.list_exercises(concept_id)
    items = [
        ExerciseListResponse(
            exercise_id=e.id,
            question_type=e.question_type,
            prompt=e.prompt,
            difficulty=e.difficulty,
            order_index=e.order_index,
            tags=e.tags,
        ).model_dump(mode="json")
        for e in exercises
    ]
    return success_response(items)


@router.put("/exercises/{exercise_id}")
async def update_exercise(
    exercise_id: str,
    body: ExerciseUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "exercise", exercise_id)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    exercise = await service.update_exercise(exercise_id, **kwargs)
    return success_response(ExerciseResponse.model_validate(exercise).model_dump(mode="json"))


@router.delete("/exercises/{exercise_id}")
async def delete_exercise(
    exercise_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "exercise", exercise_id)
    service = CourseService(session)
    await service.delete_exercise(exercise_id)
    return success_response(DeleteMessage(message="Exercise deleted successfully").model_dump())


# -----------------------------------------------------------------------
# Examples
# -----------------------------------------------------------------------

@router.post("/concepts/{concept_id}/examples", status_code=201)
async def create_example(
    concept_id: str,
    body: ExampleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "concept", concept_id)
    service = CourseService(session)
    example = await service.create_example(concept_id, **body.model_dump())
    return success_response(ExampleResponse.model_validate(example).model_dump(mode="json"))


@router.get("/concepts/{concept_id}/examples")
async def list_examples(
    concept_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    examples = await service.list_examples(concept_id)
    items = [
        ExampleBrief(
            example_id=e.id,
            content=e.content,
            explanation=e.explanation,
        ).model_dump(mode="json")
        for e in examples
    ]
    return success_response(items)


@router.put("/examples/{example_id}")
async def update_example(
    example_id: str,
    body: ExampleUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "example", example_id)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    example = await service.update_example(example_id, **kwargs)
    return success_response(ExampleResponse.model_validate(example).model_dump(mode="json"))


@router.delete("/examples/{example_id}")
async def delete_example(
    example_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "example", example_id)
    service = CourseService(session)
    await service.delete_example(example_id)
    return success_response(DeleteMessage(message="Example deleted successfully").model_dump())


# -----------------------------------------------------------------------
# Learning Objectives
# -----------------------------------------------------------------------

@router.post("/lessons/{lesson_id}/objectives", status_code=201)
async def create_objective(
    lesson_id: str,
    body: LearningObjectiveCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "lesson", lesson_id)
    service = CourseService(session)
    objective = await service.create_objective(lesson_id, **body.model_dump())
    return success_response(
        LearningObjectiveResponse.model_validate(objective).model_dump(mode="json")
    )


@router.get("/lessons/{lesson_id}/objectives")
async def list_objectives(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = CourseService(session)
    objectives = await service.list_objectives(lesson_id)
    items = [
        LearningObjectiveResponse.model_validate(obj).model_dump(mode="json")
        for obj in objectives
    ]
    return success_response(items)


@router.put("/objectives/{objective_id}")
async def update_objective(
    objective_id: str,
    body: LearningObjectiveUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "objective", objective_id)
    service = CourseService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    objective = await service.update_objective(objective_id, **kwargs)
    return success_response(
        LearningObjectiveResponse.model_validate(objective).model_dump(mode="json")
    )


@router.delete("/objectives/{objective_id}")
async def delete_objective(
    objective_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_or_admin),
) -> dict:
    await _resolve_and_verify_access(session, current_user, "objective", objective_id)
    service = CourseService(session)
    await service.delete_objective(objective_id)
    return success_response(DeleteMessage(message="Objective deleted successfully").model_dump())
