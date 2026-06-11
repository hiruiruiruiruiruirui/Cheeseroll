"""Public share endpoint — view shared notes without authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..deps import get_db
from ...models.record import Record

router = APIRouter()

from pydantic import BaseModel
from datetime import datetime


class SharedNoteResponse(BaseModel):
    id: str
    title: str
    original_markdown: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/share/{share_code}", response_model=SharedNoteResponse)
async def view_shared_note(
    share_code: str,
    db: AsyncSession = Depends(get_db),
):
    """View a shared study note by its share code. No auth required."""
    result = await db.execute(
        select(Record).where(
            Record.share_code == share_code,
            Record.status == "completed",
        )
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared note not found or has been removed",
        )

    return SharedNoteResponse(
        id=str(record.id),
        title=record.title,
        original_markdown=record.original_markdown,
        created_at=record.created_at,
    )
