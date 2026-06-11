"""Payment order Pydantic schemas."""

from datetime import datetime
import uuid
from pydantic import BaseModel


class OrderCreateRequest(BaseModel):
    """Request to create a WeChat Pay prepay order."""
    plan_type: str  # daily | monthly | quarterly


class OrderResponse(BaseModel):
    """Order details returned to frontend."""
    order_id: uuid.UUID
    plan_type: str
    amount_cents: int
    status: str
    checkout_url: str | None = None
    wx_pay_params: dict | None = None
    qr_code_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
