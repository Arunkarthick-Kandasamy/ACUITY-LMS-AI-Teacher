from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.parental_controls.schemas import ParentalControlUpdate
from app.parental_controls.service import ParentalControlService
from app.users.models import User

router = APIRouter(
    prefix=f"{settings.api_prefix}/parental-controls",
    tags=["Parental Controls"],
)


@router.get("/students/{student_id}")
async def get_student_controls(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentalControlService(session)
    controls = await service.get_controls(current_user, student_id)
    return success_response(controls.model_dump(mode="json"))


@router.patch("/students/{student_id}")
async def update_student_controls(
    student_id: str,
    body: ParentalControlUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ParentalControlService(session)
    data = body.model_dump(exclude_none=True)
    controls = await service.update_controls(current_user, student_id, data)
    return success_response(controls.model_dump(mode="json"))
