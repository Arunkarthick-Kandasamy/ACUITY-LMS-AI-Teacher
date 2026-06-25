from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.infrastructure.database import get_session

from .schemas import (
    AssessmentAnalytics,
    CourseProgressAnalytics,
    StudentProgressAnalytics,
    SystemOverview,
)
from .service import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/assessments/{course_id}", response_model=AssessmentAnalytics)
async def get_assessment_analytics(
    course_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(session)
    return await service.get_assessment_analytics(course_id)


@router.get("/students/{student_id}", response_model=StudentProgressAnalytics)
async def get_student_progress_analytics(
    student_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(session)
    return await service.get_student_progress_analytics(student_id)


@router.get("/courses/{course_id}", response_model=CourseProgressAnalytics)
async def get_course_analytics(
    course_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(session)
    return await service.get_course_analytics(course_id)


@router.get("/overview", response_model=SystemOverview)
async def get_system_overview(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(session)
    return await service.get_system_overview()
