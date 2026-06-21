from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.pacing.schemas import (
    GenerateScheduleRequest,
    PacingStatusResponse,
    PacingUpdateRequest,
    PacingUpdateResponse,
)
from app.pacing.service import PacingService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["Pacing"])


@router.post("/pacing/generate", status_code=201)
async def generate_schedule(
    body: GenerateScheduleRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = PacingService(session)
    schedule = await service.generate_schedule(
        enrollment_id=body.enrollment_id, user_id=current_user.id
    )
    return success_response(
        PacingStatusResponse(
            enrollment_id=schedule.enrollment_id,
            course_id="",
            schedule_id=schedule.id,
            current_week=schedule.current_week,
            target_lessons_per_week=schedule.target_lessons_per_week,
            pace_status=schedule.pace_status,
            last_pacing_adjustment_at=schedule.last_pacing_adjustment_at,
        ).model_dump(mode="json")
    )


@router.get("/pacing")
async def get_pacing_status(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = PacingService(session)
    statuses = await service.get_pacing_status(user_id=current_user.id)
    items = [PacingStatusResponse(**s).model_dump(mode="json") for s in statuses]
    return success_response(items)


@router.patch("/pacing")
async def update_pacing_status(
    body: PacingUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = PacingService(session)
    schedule = await service.update_pacing_status(
        user_id=current_user.id,
        enrollment_id=body.enrollment_id,
        pace_status=body.pace_status,
    )
    return success_response(
        PacingUpdateResponse(
            schedule_id=schedule.id,
            enrollment_id=schedule.enrollment_id,
            pace_status=schedule.pace_status,
            last_pacing_adjustment_at=schedule.last_pacing_adjustment_at,
        ).model_dump(mode="json")
    )
