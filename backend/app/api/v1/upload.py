"""File upload endpoint."""

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_current_user
from ...models.user import User
from ...models.file import File as FileModel
from ...schemas.file import FileUploadResponse
from ...services.file_svc import upload_file as upload_to_cos

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a study material file (.pptx, .docx, .pdf).

    Files are stored in Tencent COS with 24-hour auto-expiration.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    # Read file content
    file_data = await file.read()

    try:
        upload_result = await upload_to_cos(
            user_id=current_user.id,
            filename=file.filename,
            file_data=file_data,
            content_type=file.content_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Create file record in database
    db_file = FileModel(
        user_id=current_user.id,
        original_name=file.filename,
        file_type=upload_result["file_type"],
        file_size_bytes=upload_result["file_size_bytes"],
        cos_key=upload_result["cos_key"],
        parse_status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return FileUploadResponse(
        file_id=db_file.id,
        original_name=db_file.original_name,
        file_type=db_file.file_type,
        file_size_bytes=db_file.file_size_bytes,
        parse_status=db_file.parse_status,
    )
