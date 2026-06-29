from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import paginated_response, success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.users.models import User

from .schemas import (
    LinkStudentRequest,
    UnlinkStudentResponse,
)
from .service import ParentDashboardService

router = APIRouter(
    prefix=f"{settings.api_prefix}/parents",
    tags=["Parent Dashboard"],
)


@router.get("/students")
async def list_students(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    students = await service.get_linked_students(current_user)
    return success_response([s.model_dump(mode="json") for s in students])


@router.get("/students/{student_id}")
async def get_student(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    profile = await service.get_student_profile(current_user, student_id)
    return success_response(profile.model_dump(mode="json"))


@router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    progress = await service.get_progress_summary(current_user, student_id)
    return success_response(progress.model_dump(mode="json"))


@router.get("/students/{student_id}/curriculum")
async def get_student_curriculum(
    student_id: str,
    course_id: str = Query(..., description="Course ID to load curriculum for"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    tree = await service.get_curriculum_tree(current_user, student_id, course_id)
    return success_response(tree.model_dump(mode="json"))


@router.get("/students/{student_id}/mastery")
async def get_student_mastery(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    summary = await service.get_mastery_summary(current_user, student_id)
    return success_response(summary.model_dump(mode="json"))


@router.get("/students/{student_id}/mastery/concepts")
async def get_student_mastery_concepts(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    concepts = await service.get_mastery_by_concepts(current_user, student_id)
    return success_response([c.model_dump(mode="json") for c in concepts])


@router.get("/students/{student_id}/pacing")
async def get_student_pacing(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    pacing = await service.get_pacing(current_user, student_id)
    return success_response([p.model_dump(mode="json") for p in pacing])


@router.get("/students/{student_id}/misconceptions")
async def get_student_misconceptions(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    misconceptions = await service.get_misconceptions(current_user, student_id)
    return success_response([m.model_dump(mode="json") for m in misconceptions])


@router.get("/students/{student_id}/knowledge-gaps")
async def get_student_knowledge_gaps(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    gaps = await service.get_knowledge_gaps(current_user, student_id)
    return success_response([g.model_dump(mode="json") for g in gaps])


@router.get("/students/{student_id}/sessions")
async def get_student_sessions(
    student_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    offset = (page - 1) * per_page
    sessions, total = await service.get_sessions(
        current_user, student_id, offset=offset, limit=per_page
    )
    items = [s.model_dump(mode="json") for s in sessions]
    return paginated_response(items, total, page, per_page)


@router.get("/students/{student_id}/recent-activity")
async def get_student_recent_activity(
    student_id: str,
    days: int = Query(default=7, ge=1, le=90),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    activities = await service.get_recent_activity(current_user, student_id, days=days)
    return success_response([a.model_dump(mode="json") for a in activities])


@router.get("/students/{student_id}/dashboard")
async def get_student_dashboard(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    dashboard = await service.get_dashboard(current_user, student_id)
    return success_response(dashboard.model_dump(mode="json"))


# -----------------------------------------------------------------------
# Linking Code Management
# -----------------------------------------------------------------------

@router.post("/link-codes/generate")
async def generate_linking_code(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    result = await service.generate_linking_code(current_user)
    return success_response(result.model_dump(mode="json"))


@router.post("/link")
async def link_student(
    body: LinkStudentRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    result = await service.link_student(
        current_user, code=body.code, parent_email=body.parent_email
    )
    return success_response(result.model_dump(mode="json"))


@router.get("/pending-requests")
async def get_pending_requests(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    requests = await service.get_pending_requests(current_user)
    return success_response([r.model_dump(mode="json") for r in requests])


@router.post("/approve/{link_id}")
async def approve_link(
    link_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    result = await service.approve_link(current_user, link_id)
    return success_response(result.model_dump(mode="json"))


@router.post("/reject/{link_id}")
async def reject_link(
    link_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    result = await service.reject_link(current_user, link_id)
    return success_response(result.model_dump(mode="json"))


@router.get("/students/{student_id}/audit-log")
async def get_audit_log(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    entries = await service.get_audit_log(current_user, student_id)
    return success_response([e.model_dump(mode="json") for e in entries])


@router.delete("/students/{student_id}")
async def unlink_student(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentDashboardService(session)
    await service.unlink_student(current_user, student_id)
    return success_response(UnlinkStudentResponse(message="Student unlinked successfully").model_dump())
