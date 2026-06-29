from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.course_admin.schemas import (
    CourseBriefResponse,
    CourseDetailResponse,
    CreateCourseRequest,
    DashboardStats,
    KnowledgeSourceResponse,
    PipelineStageResponse,
    StageLogEntry,
    UpdateCourseStructureRequest,
    UpdateKnowledgeGraphRequest,
    UpdateTeachingProfileRequest,
)
from app.course_admin.service import PipelineOrchestrator
from app.infrastructure.database import get_session
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/course-admin", tags=["Course Admin"])
course_admin_only = require_roles(UserRole.COURSE_ADMIN, UserRole.ADMIN)


def _stage_to_dict(s) -> dict:
    return {
        "id": str(s.id),
        "stage_name": s.stage_name,
        "status": s.status,
        "progress_pct": s.progress_pct,
        "error_message": s.error_message,
        "output_data": s.output_data,
        "stage_logs": s.stage_logs or [],
        "retry_count": s.retry_count,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None,
        "duration_seconds": s.duration_seconds,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def _source_to_dict(s) -> dict:
    return {
        "id": str(s.id),
        "filename": s.filename or "",
        "file_type": s.file_type or "",
        "file_size": s.file_size or 0,
        "status": s.status or "",
        "error_message": s.error_message,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


async def _course_to_detail(c) -> dict:
    stages = [_stage_to_dict(s) for s in (c.stages or [])]
    sources = [_source_to_dict(s) for s in (c.sources or [])]
    sp = c.stage_progress
    return {
        "id": str(c.id),
        "name": c.name or "",
        "description": c.description,
        "status": c.status or "",
        "course_id": c.course_id,
        "stage_progress": {"completed": sp["completed"], "total": sp["total"], "pct": sp["pct"]},
        "knowledge_sources": sources,
        "knowledge_graph_data": c.knowledge_graph_data,
        "teaching_profile": c.teaching_profile,
        "course_structure": c.course_structure,
        "simulation_results": c.simulation_results,
        "error_message": c.error_message,
        "stages": stages,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _course_to_brief(c) -> dict:
    sp = c.stage_progress
    return {
        "id": str(c.id),
        "name": c.name or "",
        "description": c.description,
        "status": c.status or "",
        "course_id": c.course_id,
        "stage_progress": {"completed": sp["completed"], "total": sp["total"], "pct": sp["pct"]},
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


# -----------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------


@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    courses = await svc.list_courses(current_user)

    stats = DashboardStats(
        total_courses=len(courses),
        deployed_count=sum(1 for c in courses if c.status == "deployed"),
        training_count=sum(1 for c in courses if c.status == "training"),
        draft_count=sum(1 for c in courses if c.status == "draft"),
        review_count=sum(1 for c in courses if c.status == "review"),
        total_students=0,
        total_published=sum(1 for c in courses if c.course_id),
        active_sessions=0,
        pending_review_count=sum(1 for c in courses if c.status == "review"),
        failed_stages_count=0,
        recent_courses=[_course_to_brief(c) for c in courses[:5]],
    )

    for c in courses:
        if c.stages:
            stats.failed_stages_count += sum(1 for s in c.stages if s.status == "failed")
        structure = c.course_structure
        if structure:
            for m in structure.get("modules", []):
                for lsn in m.get("lessons", []):
                    for con in lsn.get("concepts", []):
                        if con.get("content", {}).get("explanation"):
                            stats.total_concepts_generated += 1
                        stats.total_exercises_generated += len(con.get("content", {}).get("exercises", []))

    if stats.total_concepts_generated:
        stats.avg_coverage_pct = 100.0

    return success_response(stats.model_dump(mode="json"))


# -----------------------------------------------------------------------
# Course CRUD
# -----------------------------------------------------------------------


@router.post("/courses", status_code=201)
async def create_course(
    body: CreateCourseRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    course = await svc.create_course(current_user, body.name, body.description)
    return success_response(await _course_to_detail(course))


@router.get("/courses")
async def list_courses(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    courses = await svc.list_courses(current_user)
    return success_response([_course_to_brief(c) for c in courses])


@router.get("/courses/{course_id}")
async def get_course(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    course = await svc.get_course(current_user, course_id)
    return success_response(await _course_to_detail(course))


@router.get("/courses/{course_id}/stages/{stage_name}")
async def get_stage_detail(
    course_id: str,
    stage_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    await svc.get_course(current_user, course_id)
    from app.course_admin.repository import PipelineStageRepository
    repo = PipelineStageRepository(session)
    stage = await repo.find_by_stage(course_id, stage_name)
    if stage is None:
        from app.common.exceptions import NotFoundException
        raise NotFoundException(message="Stage not found")
    return success_response(_stage_to_dict(stage))


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    await svc.delete_course(current_user, course_id)
    return success_response({"message": "Course deleted"})


# -----------------------------------------------------------------------
# Knowledge Sources
# -----------------------------------------------------------------------


@router.post("/courses/{course_id}/sources", status_code=201)
async def upload_source(
    course_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    content = await file.read()
    source = await svc.upload_source(current_user, course_id, file.filename or "untitled", content)
    return success_response(_source_to_dict(source))


# -----------------------------------------------------------------------
# Pipeline stage runner — returns immediately, processes in background
# -----------------------------------------------------------------------


@router.post("/courses/{course_id}/run/{stage_name}")
async def run_stage(
    course_id: str,
    stage_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    course = await svc.run_stage_background(current_user, course_id, stage_name)
    return success_response(await _course_to_detail(course))


# -----------------------------------------------------------------------
# Manual updates for review/editing
# -----------------------------------------------------------------------


@router.put("/courses/{course_id}/knowledge-graph")
async def update_knowledge_graph(
    course_id: str,
    body: UpdateKnowledgeGraphRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    course = await svc.update_kg(current_user, course_id, body.knowledge_graph_data)
    return success_response(await _course_to_detail(course))


@router.put("/courses/{course_id}/profile")
async def update_profile(
    course_id: str,
    body: UpdateTeachingProfileRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    course = await svc.update_profile(current_user, course_id, body.teaching_profile)
    return success_response(await _course_to_detail(course))


@router.put("/courses/{course_id}/structure")
async def update_structure(
    course_id: str,
    body: UpdateCourseStructureRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    course = await svc.update_structure(current_user, course_id, body.course_structure)
    return success_response(await _course_to_detail(course))


# -----------------------------------------------------------------------
# Retry
# -----------------------------------------------------------------------


@router.post("/courses/{course_id}/retry/{stage_name}")
async def retry_stage(
    course_id: str,
    stage_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(course_admin_only),
) -> dict:
    svc = PipelineOrchestrator(session)
    course = await svc.retry_stage(current_user, course_id, stage_name)
    return success_response(await _course_to_detail(course))
