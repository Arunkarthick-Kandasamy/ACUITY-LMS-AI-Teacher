from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import paginated_response, success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.users.models import User

from .schemas import ReportResponse
from .service import ReportService

router = APIRouter(
    prefix=f"{settings.api_prefix}/reports",
    tags=["Reports"],
)


@router.post("/generate/{student_id}")
async def generate_report(
    student_id: str = Path(..., description="Student ID to generate report for"),
    report_type: str = Query(default="weekly", description="Report type: weekly, monthly, milestone"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ReportService(session)
    report = await service.generate_report(current_user, student_id, report_type)
    return success_response(report.model_dump(mode="json"))


@router.get("/{report_id}")
async def get_report(
    report_id: str = Path(..., description="Report ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ReportService(session)
    report = await service.get_report(current_user, report_id)
    return success_response(report.model_dump(mode="json"))


@router.get("/student/{student_id}")
async def list_student_reports(
    student_id: str = Path(..., description="Student ID"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = ReportService(session)
    items, total = await service.get_student_reports(
        current_user, student_id, page=page, per_page=per_page
    )
    serialized = [i.model_dump(mode="json") for i in items]
    return paginated_response(serialized, total, page, per_page)
