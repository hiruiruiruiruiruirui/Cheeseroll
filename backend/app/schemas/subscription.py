"""Subscription Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel


class PlanInfo(BaseModel):
    """Public plan listing (no auth required)."""
    plan_type: str
    name: str
    price_cents: int
    duration_days: int
    daily_quota: int
    features: list[str]
    is_active: bool = True

    model_config = {"from_attributes": True}


class SubscriptionStatus(BaseModel):
    """Current user's subscription status."""
    has_subscription: bool
    plan_type: str | None = None
    plan_name: str | None = None
    status: str | None = None                    # active | expired | cancelled
    start_date: datetime | None = None
    end_date: datetime | None = None
    daily_quota: int | None = None
    daily_used: int | None = None
    remaining_today: int | None = None
    quota_reset_at: datetime | None = None
    trial_used: bool = False


class SubscriptionActivate(BaseModel):
    """Used internally to activate/update a subscription after payment."""
    plan_type: str
    duration_days: int
    daily_quota: int
