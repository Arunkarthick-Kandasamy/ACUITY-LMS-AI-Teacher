from __future__ import annotations

from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base import Base, TimestampMixin, UUIDMixin


class PaymentPlan(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "payment_plans"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_monthly: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_yearly: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    max_students: Mapped[int] = mapped_column(default=0, nullable=False)
    features: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Subscription(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("payment_plans.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, cancelled, expired, trial
    billing_cycle: Mapped[str] = mapped_column(String(10), default="monthly", nullable=False)
    current_period_start: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    current_period_end: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
