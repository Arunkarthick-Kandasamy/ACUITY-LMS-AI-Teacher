from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import paginated_response, success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.progress.schemas import (
    AttemptCreate,
    AttemptHistoryItem,
    AttemptResponse,
    CurriculumLesson,
    CurriculumModule,
    CurriculumTreeResponse,
    LessonProgressResponse,
    LessonProgressUpdate,
)
from app.progress.service import ProgressService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["Progress"])


@router.get("/courses/{course_id}/curriculum")
async def get_curriculum_tree(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ProgressService(session)
    course = await service.get_curriculum_tree(course_id)
    modules = []
    for m in course.modules:
        lessons = []
        for lsn in m.lessons:
            lessons.append(
                CurriculumLesson(
                    lesson_id=lsn.id,
                    title=lsn.title,
                    order_index=lsn.order_index,
                    status=lsn.status.value if lsn.status else None,
                    estimated_duration_minutes=lsn.estimated_duration_minutes,
                ).model_dump(mode="json")
            )
        modules.append(
            CurriculumModule(
                module_id=m.id,
                title=m.title,
                order_index=m.order_index,
                lesson_count=len(lessons),
            ).model_dump(mode="json")
        )
    return success_response(
        CurriculumTreeResponse(
            course_id=course.id,
            course_title=course.title,
            course_code=course.code,
            modules=modules,
        ).model_dump(mode="json")
    )


@router.get("/lessons/{lesson_id}/progress")
async def get_lesson_progress(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ProgressService(session)
    progress = await service.get_lesson_progress(
        lesson_id=lesson_id, user_id=current_user.id
    )
    if progress is None:
        return success_response(None)
    return success_response(
        LessonProgressResponse.model_validate(progress).model_dump(mode="json")
    )


@router.patch("/lessons/{lesson_id}/progress")
async def update_lesson_progress(
    lesson_id: str,
    body: LessonProgressUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ProgressService(session)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    progress = await service.update_lesson_progress(
        lesson_id=lesson_id, user_id=current_user.id, **kwargs
    )
    return success_response(
        LessonProgressResponse.model_validate(progress).model_dump(mode="json")
    )


@router.post("/exercises/{exercise_id}/attempts", status_code=201)
async def record_attempt(
    exercise_id: str,
    body: AttemptCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ProgressService(session)
    kwargs = body.model_dump()
    kwargs.pop("exercise_id", None)
    attempt = await service.record_attempt(
        user_id=current_user.id, exercise_id=exercise_id, **kwargs
    )
    return success_response(
        AttemptResponse.model_validate(attempt).model_dump(mode="json")
    )


@router.get("/attempts")
async def get_attempt_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ProgressService(session)
    attempts, total = await service.get_attempt_history(
        user_id=current_user.id, page=page, per_page=per_page
    )
    items = []
    for a in attempts:
        exercise = a.exercise if hasattr(a, "exercise") else None
        items.append(
            AttemptHistoryItem(
                attempt_id=a.id,
                exercise_id=a.exercise_id,
                question_type=exercise.question_type if exercise else None,
                prompt=exercise.prompt if exercise else None,
                is_correct=a.is_correct,
                score=a.score,
                attempt_number=a.attempt_number,
                attempted_at=a.attempted_at,
            ).model_dump(mode="json")
        )
    return paginated_response(items, total, page, per_page)
