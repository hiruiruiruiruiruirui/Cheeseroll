"""Payment API — Lemon Squeezy checkout."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_current_user
from ...models.user import User
from ...schemas.order import OrderCreateRequest, OrderResponse
from ...schemas.payment import PaymentCallbackResult
from ...services import payment_svc
from ...config import settings

router = APIRouter()


@router.post("/payment/order", response_model=OrderResponse)
async def create_payment_order(
    req: OrderCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a payment order and return Lemon Squeezy checkout URL."""
    try:
        result = await payment_svc.create_order(db, user_id=user.id, plan_type=req.plan_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return OrderResponse(**result)


@router.post("/payment/webhook")
async def ls_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Lemon Squeezy webhook — auto-activates subscription on payment."""
    payload = await request.body()
    signature = request.headers.get("x-signature", "")
    try:
        result = await payment_svc.handle_lemonsqueezy_webhook(payload, signature)
        if result.get("order_id"):
            await payment_svc.activate_paid_order(db, result["order_id"])
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/payment/dev-activate")
async def dev_activate(
    req: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dev-only: manually activate subscription."""
    if settings.APP_ENV != "development":
        raise HTTPException(status_code=404)
    plan_type = req.get("plan_type", "monthly")
    plan = payment_svc.PLAN_PRICES.get(plan_type)
    if not plan:
        raise HTTPException(400, detail="Invalid plan")
    from ...services import subscription_svc
    sub = await subscription_svc.activate_subscription(db, user_id=user.id, plan_type=plan_type,
        duration_days=plan["duration_days"], daily_quota=plan["daily_quota"])
    return {"status": "activated", "plan_type": plan_type}
