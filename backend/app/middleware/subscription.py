"""Subscription middleware — FastAPI dependency for quota enforcement."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.deps import get_current_user, get_db
from ..config import settings
from ..models.user import User
from ..services import subscription_svc


async def require_quota(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Ensure the current user has remaining processing quota.

    In development mode, quota checks are bypassed.
    """
    if settings.APP_ENV == "development":
        return user

    # Admin bypass
    if user.role == "admin":
        return user

    allowed, reason, _remaining = await subscription_svc.check_quota(db, user)

    if not allowed:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "quota_exceeded",
                "message": reason,
                "code": "SUBSCRIBE_REQUIRED",
            },
        )

    return user


async def require_quarterly(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Ensure the current user has a quarterly subscription (for premium features)."""
    if settings.APP_ENV == "development" or user.role == "admin":
        return user
    sub = await subscription_svc.get_user_subscription(db, user.id)

    if sub is None or sub.status != "active" or sub.plan_type not in ("quarterly",):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "premium_feature",
                "message": "此功能需要包季度订阅",
                "code": "UPGRADE_REQUIRED",
            },
        )

    return user


async def get_subscription_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Convenience dependency that returns the full subscription status dict."""
    return await subscription_svc.build_subscription_status(db, user)
