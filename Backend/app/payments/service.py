from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, NotFoundException
from app.payments.models import PaymentPlan, Subscription
from app.payments.repository import PaymentPlanRepository, SubscriptionRepository
from app.payments.schemas import PlanResponse, SubscriptionResponse
from app.users.models import User


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.plan_repo = PaymentPlanRepository(session)
        self.sub_repo = SubscriptionRepository(session)

    async def create_plan(self, name: str, description: str | None, price_monthly: float, price_yearly: float, currency: str, max_students: int, features: str | None) -> PlanResponse:
        plan = PaymentPlan(
            name=name, description=description,
            price_monthly=price_monthly, price_yearly=price_yearly,
            currency=currency, max_students=max_students, features=features,
        )
        self.session.add(plan)
        await self.session.flush()
        return PlanResponse.model_validate(plan)

    async def list_plans(self, active_only: bool = True) -> list[PlanResponse]:
        plans = await self.plan_repo.find_active() if active_only else await self.plan_repo.list()
        return [PlanResponse.model_validate(p) for p in plans]

    async def subscribe(self, user: User, plan_id: str, billing_cycle: str) -> SubscriptionResponse:
        plan = await self.plan_repo.get(plan_id)
        if plan is None:
            raise NotFoundException(message="Plan not found")
        existing = await self.sub_repo.find_active_by_user(user.id)
        if existing:
            raise ConflictException(message="Already have an active subscription")
        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=365 if billing_cycle == "yearly" else 30)
        sub = Subscription(
            user_id=user.id, plan_id=plan_id,
            billing_cycle=billing_cycle,
            current_period_start=now, current_period_end=period_end,
        )
        self.session.add(sub)
        await self.session.flush()
        resp = SubscriptionResponse.model_validate(sub)
        resp.plan_name = plan.name
        return resp

    async def my_subscription(self, user: User) -> SubscriptionResponse | None:
        sub = await self.sub_repo.find_active_by_user(user.id)
        if sub is None:
            return None
        plan = await self.plan_repo.get(sub.plan_id)
        resp = SubscriptionResponse.model_validate(sub)
        if plan:
            resp.plan_name = plan.name
        return resp

    async def cancel_subscription(self, user: User) -> SubscriptionResponse:
        sub = await self.sub_repo.find_active_by_user(user.id)
        if sub is None:
            raise NotFoundException(message="No active subscription found")
        sub.status = "cancelled"
        sub.cancelled_at = datetime.now(timezone.utc)
        await self.session.flush()
        plan = await self.plan_repo.get(sub.plan_id)
        resp = SubscriptionResponse.model_validate(sub)
        if plan:
            resp.plan_name = plan.name
        return resp
