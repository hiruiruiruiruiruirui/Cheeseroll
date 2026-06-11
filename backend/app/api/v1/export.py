"""PDF export endpoints."""

import uuid, os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..deps import get_db, get_current_user
from ...models.user import User
from ...models.record import Record
from ...services.file_svc import get_download_url

router = APIRouter()


@router.get("/records/{record_id}/pdf")
async def download_pdf(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download PDF for a record. Generates PDF on-the-fly if not cached."""
    result = await db.execute(
        select(Record).where(Record.id == record_id, Record.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not ready: {record.status}")
    if not record.original_markdown:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No content to generate PDF")

    # Generate PDF on-the-fly from markdown
    from ...services.pdf_exporter import markdown_to_pdf
    pdf_bytes = await markdown_to_pdf(record.original_markdown, title=record.title)

    # Save locally and return
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(pdf_bytes)
    tmp.close()

    filename = f"{record.title[:50]}_notes.pdf"
    return FileResponse(tmp.name, media_type="application/pdf", filename=filename)
