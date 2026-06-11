"""Payment callback schemas."""

from pydantic import BaseModel


class WechatPayCallback(BaseModel):
    """WeChat Pay V3 callback body (parsed after signature verification)."""
    id: str                       # notification unique ID
    create_time: str              # notification creation time
    resource_type: str            # "encrypt-resource"
    event_type: str               # e.g. "TRANSACTION.SUCCESS"
    resource: dict                # { algorithm, ciphertext, associated_data, nonce, original_type }


class PaymentCallbackResult(BaseModel):
    """Result returned after processing the payment callback."""
    order_id: str
    status: str
    plan_activated: bool
