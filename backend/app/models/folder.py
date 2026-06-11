"""Folder model for organizing study records."""

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin


class Folder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "folders"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
