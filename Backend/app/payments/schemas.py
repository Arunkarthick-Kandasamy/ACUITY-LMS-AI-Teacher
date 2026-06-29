from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    description: str | None = None
    price_monthly: float
    price_yearly: float
    currency: str = "USD"
    max_students: int = 0
    features: str | None = None


class PlanResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    price_monthly: float
    price_yearly: float
    currency: str
    max_students: int
    features: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class SubscriptionResponse(BaseModel):
    id: str
    plan_id: str
    plan_name: str = ""
    status: str
    billing_cycle: str
    current_period_start: datetime
    current_period_end: datetime | None = None
    cancelled_at: datetime | None = None

    model_config = {"from_attributes": True}


class SubscribeRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"
