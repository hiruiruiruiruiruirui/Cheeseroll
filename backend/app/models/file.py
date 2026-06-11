"""Uploaded file model."""

from datetime import datetime
import uuid
from sqlalchemy import String, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, UUIDMixin, TimestampMixin


class File(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "files"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    original_name: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(20))  # pptx | docx | pdf
    file_size_bytes: Mapped[int] = mapped_column(BigInteger)
    cos_key: Mapped[str] = mapped_column(String(500))
    parse_status: Mapped[str] = mapped_column(String(20), default="pending")
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
