from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.enrollment.schemas import EnrollmentCreate, EnrollmentListResponse, EnrollmentResponse
from app.enrollment.service import EnrollmentService
from app.infrastructure.database import get_session
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["Enrollment"])


def _enrich_enrollment(enrollment) -> dict:
    course_title = enrollment.course.title if hasattr(enrollment, "course") and enrollment.course else None
    return EnrollmentResponse(
        enrollment_id=enrollment.id,
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
        course_title=course_title,
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at,
        started_at=enrollment.started_at,
        target_completion_date=enrollment.target_completion_date,
        completed_at=enrollment.completed_at,
    ).model_dump(mode="json")


@router.post("/enrollments", status_code=201)
async def enroll(
    body: EnrollmentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.STUDENT)),
) -> dict:
    service = EnrollmentService(session)
    enrollment = await service.enroll(user_id=current_user.id, course_id=body.course_id)
    return success_response(_enrich_enrollment(enrollment))


@router.get("/enrollments")
async def list_enrollments(
    student_id: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = EnrollmentService(session)
    is_admin = current_user.role == UserRole.ADMIN

    enrollments = await service.list_enrollments(
        user_id=current_user.id, is_admin=is_admin, student_id=student_id
    )
    items = []
    for e in enrollments:
        course_title = e.course.title if hasattr(e, "course") and e.course else None
        course_code = e.course.code if hasattr(e, "course") and e.course else None
        items.append(
            EnrollmentListResponse(
                enrollment_id=e.id,
                course_id=e.course_id,
                course_title=course_title,
                course_code=course_code,
                status=e.status,
                enrolled_at=e.enrolled_at,
                target_completion_date=e.target_completion_date,
            ).model_dump(mode="json")
        )
    return success_response(items)


@router.get("/enrollments/{enrollment_id}")
async def get_enrollment(
    enrollment_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = EnrollmentService(session)
    is_admin = current_user.role == UserRole.ADMIN
    enrollment = await service.get_enrollment(
        enrollment_id, user_id=current_user.id, is_admin=is_admin
    )
    return success_response(_enrich_enrollment(enrollment))
