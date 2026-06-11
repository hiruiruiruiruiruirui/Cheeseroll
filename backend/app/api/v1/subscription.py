"""Subscription API endpoints — plan listing, status, quota."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_current_user
from ...models.user import User
from ...schemas.subscription import PlanInfo, SubscriptionStatus
from ...services import subscription_svc
from ...services.subscription_svc import build_subscription_status

router = APIRouter()


@router.get("/plans", response_model=list[PlanInfo])
async def list_plans(
    db: AsyncSession = Depends(get_db),
):
    """List all available subscription plans. Public endpoint — no auth required."""
    plans = await subscription_svc.get_plans(db)
    return [
        PlanInfo(
            plan_type=p.plan_type,
            name=p.name,
            price_cents=p.price_cents,
            duration_days=p.duration_days,
            daily_quota=p.daily_quota,
            features=p.features,
            is_active=p.is_active,
        )
        for p in plans
    ]


@router.get("/subscription/status", response_model=SubscriptionStatus)
async def get_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's subscription status and quota."""
    status_dict = await build_subscription_status(db, user)
    return SubscriptionStatus(**status_dict)
