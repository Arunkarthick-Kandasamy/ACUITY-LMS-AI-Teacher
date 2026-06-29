from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.database import get_session
from app.payments.schemas import PlanCreate, SubscribeRequest
from app.payments.service import PaymentService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/payments", tags=["Payments"])


@router.post("/plans")
async def create_plan(
    body: PlanCreate,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = PaymentService(session)
    plan = await svc.create_plan(body.name, body.description, body.price_monthly, body.price_yearly, body.currency, body.max_students, body.features)
    return success_response(plan.model_dump(mode="json"))


@router.get("/plans")
async def list_plans(
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(get_current_active_user),
) -> dict:
    svc = PaymentService(session)
    plans = await svc.list_plans(active_only=True)
    return success_response([p.model_dump(mode="json") for p in plans])


@router.post("/subscribe")
async def subscribe(
    body: SubscribeRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    svc = PaymentService(session)
    sub = await svc.subscribe(current_user, body.plan_id, body.billing_cycle)
    return success_response(sub.model_dump(mode="json"))


@router.get("/subscription")
async def my_subscription(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    svc = PaymentService(session)
    sub = await svc.my_subscription(current_user)
    return success_response(sub.model_dump(mode="json") if sub else None)


@router.post("/cancel")
async def cancel_subscription(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    svc = PaymentService(session)
    sub = await svc.cancel_subscription(current_user)
    return success_response(sub.model_dump(mode="json"))
