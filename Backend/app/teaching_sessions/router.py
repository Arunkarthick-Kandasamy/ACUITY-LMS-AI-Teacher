from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import paginated_response, success_response
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.database import get_session
from app.teaching_sessions.schemas import EndSessionRequest, SessionHistoryItem, SessionResponse, StartSessionRequest
from app.teaching_sessions.service import SessionService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["Teaching Sessions"])


def _enrich_session(session) -> dict:
    course_title = (
        session.course.title
        if hasattr(session, "course") and session.course
        else None
    )
    return SessionResponse(
        session_id=session.id,
        student_id=session.student_id,
        course_id=session.course_id,
        course_title=course_title,
        current_lesson_id=session.current_lesson_id,
        current_concept_id=session.current_concept_id,
        state=session.state,
        context=session.context or {},
        started_at=session.started_at,
        last_activity_at=session.last_activity_at,
        completed_at=session.completed_at,
    ).model_dump(mode="json")


@router.post("/sessions", status_code=201)
async def start_session(
    body: StartSessionRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = SessionService(session)
    teaching_session = await service.start_session(
        user_id=current_user.id,
        course_id=body.course_id,
        lesson_id=body.lesson_id,
        concept_id=body.concept_id,
    )
    return success_response(_enrich_session(teaching_session))


@router.get("/sessions/current")
async def resume_session(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = SessionService(session)
    teaching_session = await service.resume_session(user_id=current_user.id)
    return success_response(_enrich_session(teaching_session))


@router.patch("/sessions/{session_id}/pause")
async def pause_session(
    session_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = SessionService(session)
    teaching_session = await service.pause_session(
        session_id=session_id, user_id=current_user.id
    )
    return success_response(_enrich_session(teaching_session))


@router.patch("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    body: EndSessionRequest | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = SessionService(session)
    teaching_session = await service.end_session(
        session_id=session_id, user_id=current_user.id
    )
    return success_response(_enrich_session(teaching_session))


@router.get("/sessions/history")
async def get_session_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    student_id: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = SessionService(session)
    is_admin = current_user.role == UserRole.ADMIN

    sessions, total = await service.get_session_history(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        is_admin=is_admin,
        student_id=student_id,
    )
    items = []
    for s in sessions:
        course_title = (
            s.course.title
            if hasattr(s, "course") and s.course
            else None
        )
        duration_minutes = None
        if s.started_at and s.completed_at:
            delta = s.completed_at - s.started_at
            duration_minutes = int(delta.total_seconds() // 60)

        items.append(
            SessionHistoryItem(
                session_id=s.id,
                course_id=s.course_id,
                course_title=course_title,
                state=s.state,
                started_at=s.started_at,
                last_activity_at=s.last_activity_at,
                completed_at=s.completed_at,
                duration_minutes=duration_minutes,
            ).model_dump(mode="json")
        )
    return paginated_response(items, total, page, per_page)
