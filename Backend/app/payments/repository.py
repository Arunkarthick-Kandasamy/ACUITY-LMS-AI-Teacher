from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.payments.models import PaymentPlan, Subscription


class PaymentPlanRepository(Repository[PaymentPlan]):
    def __init__(self, session) -> None:
        super().__init__(PaymentPlan, session)

    async def find_active(self) -> list[PaymentPlan]:
        stmt = select(PaymentPlan).where(PaymentPlan.is_active == True).order_by(PaymentPlan.price_monthly)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class SubscriptionRepository(Repository[Subscription]):
    def __init__(self, session) -> None:
        super().__init__(Subscription, session)

    async def find_active_by_user(self, user_id: str) -> Subscription | None:
        stmt = select(Subscription).where(Subscription.user_id == user_id, Subscription.status == "active")
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_user(self, user_id: str) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
