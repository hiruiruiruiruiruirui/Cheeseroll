"""Payment service — Lemon Squeezy checkout + webhook."""
import uuid, hmac, hashlib, json
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..models.order import Order
from . import subscription_svc

def _utcnow(): return datetime.now(timezone.utc)

PLAN_PRICES = {
    "daily":     {"price_cents": 990,  "duration_days": 1,  "daily_quota": 1},
    "monthly":   {"price_cents": 4900, "duration_days": 30, "daily_quota": 10},
    "quarterly": {"price_cents": 9900, "duration_days": 90, "daily_quota": 10},
}

# Lemon Squeezy checkout URLs per plan
CHECKOUT_URLS = {
    "daily":     "https://mindrolltech.lemonsqueezy.com/checkout/buy/3cbe73b7-49d1-40a6-bc67-9b3d3430d791",
    "monthly":   "https://mindrolltech.lemonsqueezy.com/checkout/buy/749be464-54a0-4d40-81be-518df51181f0",
    "quarterly": "https://mindrolltech.lemonsqueezy.com/checkout/buy/6a0a8afe-904c-448a-88fe-bd3f21d6a189",
}


async def create_order(db: AsyncSession, user_id: str, plan_type: str) -> dict:
    plan = PLAN_PRICES.get(plan_type)
    if not plan:
        raise ValueError(f"Unknown plan type: {plan_type}")

    order = Order(user_id=user_id, plan_type=plan_type, amount_cents=plan["price_cents"], status="pending")
    db.add(order)
    await db.commit()
    await db.refresh(order)

    checkout_url = CHECKOUT_URLS.get(plan_type) or _mock_prepay_params(order).get("checkout_url")

    return {
        "order_id": str(order.id), "plan_type": plan_type, "amount_cents": plan["price_cents"],
        "status": order.status, "checkout_url": checkout_url,
        "created_at": order.created_at,
    }


async def handle_lemonsqueezy_webhook(payload: bytes, signature: str) -> dict:
    """Verify Lemon Squeezy webhook and extract order info."""
    secret = settings.LEMON_SQUEEZY_WEBHOOK_SECRET
    if secret:
        computed = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(computed, signature):
            raise ValueError("Invalid webhook signature")

    data = json.loads(payload)
    event_name = data.get("meta", {}).get("event_name", "")
    order_data = data.get("data", {})

    if event_name == "order_created":
        custom = order_data.get("attributes", {}).get("custom_data", {})
        return {"event": "order_created", "order_id": custom.get("order_id"),
                "email": order_data.get("attributes", {}).get("user_email")}

    return {"event": event_name, "status": "ignored"}


async def activate_paid_order(db: AsyncSession, order_id: str) -> dict:
    result = await db.execute(select(Order).where(Order.id == uuid.UUID(order_id)))
    order = result.scalar_one_or_none()
    if not order: raise ValueError(f"Order not found: {order_id}")
    if order.status == "paid": return {"order_id": str(order.id), "status": "already_paid"}

    order.status = "paid"; order.paid_at = _utcnow()
    plan = PLAN_PRICES.get(order.plan_type)
    if plan:
        await subscription_svc.activate_subscription(db, user_id=order.user_id, plan_type=order.plan_type,
            duration_days=plan["duration_days"], daily_quota=plan["daily_quota"])
    await db.commit()
    return {"order_id": str(order.id), "status": "paid", "plan_activated": True}


async def handle_payment_callback(db: AsyncSession, callback_data: dict) -> dict:
    out_trade_no = callback_data.get("out_trade_no")
    if not out_trade_no: return {"status": "error"}
    return await activate_paid_order(db, out_trade_no)


def _mock_prepay_params(order: Order) -> dict:
    return {"checkout_url": None, "pay_params": {"mock": True}}
