"""Subscription service — plan lookup, quota checks, activation, expiry."""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.subscription import Subscription, SubscriptionPlan
from ..models.user import User


def _utcnow():
    return datetime.now(timezone.utc)


async def get_plans(db: AsyncSession) -> list[SubscriptionPlan]:
    """List all active subscription plans."""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.is_active == True).order_by(SubscriptionPlan.price_cents)
    )
    return list(result.scalars().all())


async def get_plan_by_type(db: AsyncSession, plan_type: str) -> SubscriptionPlan | None:
    """Look up a plan by its type string."""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.plan_type == plan_type)
    )
    return result.scalar_one_or_none()


async def get_user_subscription(db: AsyncSession, user_id: str) -> Subscription | None:
    """Return the user's active subscription record, if any."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def check_quota(db: AsyncSession, user: User) -> tuple[bool, str, int | None]:
    """Check whether the user is allowed to process a document.

    Returns:
        (allowed, reason, remaining_today)

    Rules:
        1. Active subscription with remaining daily quota → allowed
        2. Active subscription, quota exhausted → denied until reset
        3. Expired subscription → trial logic
        4. No subscription + trial unused → allowed once (trial)
        5. No subscription + trial used → denied, need subscription
    """
    sub = await get_user_subscription(db, user.id)

    # --- Has an active subscription ---
    if sub is not None and sub.status == "active":
        now = _utcnow()

        # Check if subscription itself has expired
        if sub.end_date <= now:
            sub.status = "expired"
            await db.commit()
            # Fall through to trial logic below
        else:
            # Reset daily quota if the reset window has passed
            if sub.quota_reset_at is None or sub.quota_reset_at <= now:
                sub.daily_used = 0
                sub.quota_reset_at = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                # If we just passed midnight, set reset to next midnight
                if sub.quota_reset_at <= now:
                    from datetime import timedelta
                    sub.quota_reset_at = (_utcnow() + timedelta(days=1)).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                await db.commit()

            remaining = sub.daily_quota - sub.daily_used
            if remaining > 0:
                return True, "ok", remaining
            else:
                reset_str = sub.quota_reset_at.strftime("%H:%M") if sub.quota_reset_at else "明天"
                return False, f"今日配额已用完，{reset_str} 重置", 0

    # --- No active subscription → trial logic (3 free uses) ---
    MAX_TRIAL = 3
    if user.trial_count < MAX_TRIAL:
        remaining_trials = MAX_TRIAL - user.trial_count
        return True, "trial", remaining_trials
    else:
        user.trial_used = True
        return False, "试用已用完，请订阅后继续使用", 0


async def consume_quota(db: AsyncSession, user: User) -> bool:
    """Consume one quota unit. Returns True if successful, False if denied."""
    allowed, reason, remaining = await check_quota(db, user)

    if not allowed:
        return False

    if reason == "trial":
        user.trial_count += 1
        if user.trial_count >= 3:
            user.trial_used = True
        await db.commit()
        return True

    sub = await get_user_subscription(db, user.id)
    if sub is None:
        return False

    sub.daily_used += 1
    await db.commit()
    return True


async def activate_subscription(
    db: AsyncSession,
    user_id: str,
    plan_type: str,
    duration_days: int,
    daily_quota: int,
) -> Subscription:
    """Create or extend a subscription for the user."""
    sub = await get_user_subscription(db, user_id)
    now = _utcnow()

    if sub is None:
        from datetime import timedelta
        sub = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            status="active",
            start_date=now,
            end_date=now + timedelta(days=duration_days),
            daily_quota=daily_quota,
            daily_used=0,
            quota_reset_at=(now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
        )
        db.add(sub)
    else:
        # Extend: if currently active, add days to existing end_date; otherwise start fresh
        from datetime import timedelta
        if sub.status == "active" and sub.end_date > now:
            sub.end_date = sub.end_date + timedelta(days=duration_days)
        else:
            sub.start_date = now
            sub.end_date = now + timedelta(days=duration_days)
        sub.plan_type = plan_type
        sub.status = "active"
        sub.daily_quota = daily_quota
        sub.daily_used = 0

    await db.commit()
    await db.refresh(sub)
    return sub


async def build_subscription_status(db: AsyncSession, user: User) -> dict:
    """Build the full subscription status response for a user."""
    sub = await get_user_subscription(db, user.id)
    now = _utcnow()

    if sub is None or sub.status != "active" or sub.end_date <= now:
        return {
            "has_subscription": False,
            "plan_type": sub.plan_type if sub else None,
            "plan_name": None,
            "status": sub.status if sub else None,
            "start_date": sub.start_date if sub else None,
            "end_date": sub.end_date if sub else None,
            "daily_quota": None,
            "daily_used": None,
            "remaining_today": None,
            "quota_reset_at": None,
            "trial_used": user.trial_used,
        }

    # Determine remaining
    allowed, _, remaining = await check_quota(db, user)

    # Look up plan name
    plan = await get_plan_by_type(db, sub.plan_type)
    plan_name = plan.name if plan else sub.plan_type

    return {
        "has_subscription": True,
        "plan_type": sub.plan_type,
        "plan_name": plan_name,
        "status": sub.status,
        "start_date": sub.start_date,
        "end_date": sub.end_date,
        "daily_quota": sub.daily_quota,
        "daily_used": sub.daily_used,
        "remaining_today": remaining if allowed else 0,
        "quota_reset_at": sub.quota_reset_at,
        "trial_used": user.trial_used,
    }
