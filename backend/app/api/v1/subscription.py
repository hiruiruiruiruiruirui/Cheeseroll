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
    if not plans:
        # Fallback hardcoded plans
        return [
            PlanInfo(plan_type="daily", name="Daily", price_cents=990, duration_days=1, daily_quota=1, features=["1 processing","1 PDF"], is_active=True),
            PlanInfo(plan_type="monthly", name="Monthly", price_cents=4900, duration_days=30, daily_quota=10, features=["Unlimited processing","Unlimited exports","Multi-format"], is_active=True),
            PlanInfo(plan_type="quarterly", name="Quarterly", price_cents=9900, duration_days=90, daily_quota=10, features=["Unlimited processing","Unlimited exports","Multi-format","Wrong-answer book","Learning paths"], is_active=True),
        ]
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
