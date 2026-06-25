from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import paginated_response, success_response
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.database import get_session
from app.users.models import User

from .service import TeacherService

router = APIRouter(
    prefix=f"{settings.api_prefix}/teacher",
    tags=["Teacher"],
)


@router.get("/students")
async def list_students(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    students = await service.list_students(current_user)
    return success_response([s.model_dump(mode="json") for s in students])


@router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    progress = await service.get_student_progress(current_user, student_id)
    return success_response(progress.model_dump(mode="json"))


@router.get("/students/{student_id}/mastery")
async def get_student_mastery(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    mastery = await service.get_student_mastery(current_user, student_id)
    return success_response(mastery.model_dump(mode="json"))


@router.get("/students/{student_id}/misconceptions")
async def get_student_misconceptions(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    misconceptions = await service.get_student_misconceptions(current_user, student_id)
    return success_response([m.model_dump(mode="json") for m in misconceptions])


@router.get("/students/{student_id}/sessions")
async def get_student_sessions(
    student_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    offset = (page - 1) * per_page
    sessions, total = await service.get_student_sessions(
        current_user, student_id, offset=offset, limit=per_page
    )
    items = [s.model_dump(mode="json") for s in sessions]
    return paginated_response(items, total, page, per_page)


@router.get("/students/{student_id}/attempts")
async def get_student_attempts(
    student_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    offset = (page - 1) * per_page
    attempts, total = await service.get_student_attempts(
        current_user, student_id, offset=offset, limit=per_page
    )
    items = [a.model_dump(mode="json") for a in attempts]
    return paginated_response(items, total, page, per_page)


@router.get("/courses")
async def list_courses(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    courses = await service.list_courses(current_user)
    return success_response([c.model_dump(mode="json") for c in courses])


@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
) -> dict:
    service = TeacherService(session)
    dashboard = await service.get_dashboard(current_user)
    return success_response(dashboard.model_dump(mode="json"))
