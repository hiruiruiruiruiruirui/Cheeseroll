"""AI-generated study record model."""

import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, UUIDMixin, TimestampMixin


class Record(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "records"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    file_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    original_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_cos_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="processing")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    share_code: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    folder_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
