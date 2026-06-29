from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.database import get_session
from app.institutional.schemas import AddDomainRequest, SchoolCreate, SchoolUpdate
from app.institutional.service import InstitutionalService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/institutional", tags=["Institutional"])


@router.post("/schools")
async def create_school(
    body: SchoolCreate,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = InstitutionalService(session)
    school = await svc.create_school(body.name, body.code, body.address, body.phone, body.domains)
    return success_response(school.model_dump(mode="json"))


@router.get("/schools")
async def list_schools(
    active_only: bool = False,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = InstitutionalService(session)
    schools = await svc.list_schools(active_only)
    return success_response([s.model_dump(mode="json") for s in schools])


@router.get("/schools/{school_id}")
async def get_school(
    school_id: str,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = InstitutionalService(session)
    school = await svc.get_school(school_id)
    return success_response(school.model_dump(mode="json"))


@router.patch("/schools/{school_id}")
async def update_school(
    school_id: str,
    body: SchoolUpdate,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = InstitutionalService(session)
    school = await svc.update_school(school_id, body.name, body.address, body.phone, body.is_active)
    return success_response(school.model_dump(mode="json"))


@router.post("/schools/{school_id}/domains")
async def add_domain(
    school_id: str,
    body: AddDomainRequest,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = InstitutionalService(session)
    school = await svc.add_domain(school_id, body.domain, body.is_primary)
    return success_response(school.model_dump(mode="json"))
