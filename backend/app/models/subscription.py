"""Subscription model — tracks user subscription state."""

from datetime import datetime
import uuid
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, UUIDMixin, TimestampMixin


class SubscriptionPlan(Base):
    """Static plan definitions (seeded in DB — see scripts/seed_subscription_plans.sql)."""

    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_type: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_quota: Mapped[int] = mapped_column(Integer, nullable=False)
    features: Mapped[dict] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(default=True)


class Subscription(Base, UUIDMixin, TimestampMixin):
    """Per-user subscription state."""

    __tablename__ = "subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    plan_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | expired | cancelled
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    daily_quota: Mapped[int] = mapped_column(Integer, default=10)
    daily_used: Mapped[int] = mapped_column(Integer, default=0)
    quota_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
