"""Payment order model."""

from datetime import datetime
import uuid
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, UUIDMixin, TimestampMixin


class Order(Base, UUIDMixin, TimestampMixin):
    """WeChat Pay order tracking."""

    __tablename__ = "orders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | paid | refunded | closed
    wx_transaction_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    wx_prepay_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
