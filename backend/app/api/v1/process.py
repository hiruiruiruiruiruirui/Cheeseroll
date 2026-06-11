"""Processing endpoints — start AI processing and poll status."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..deps import get_db, get_current_user
from ...config import settings
from ...middleware.subscription import require_quota
from ...models.user import User
from ...models.file import File as FileModel
from ...models.record import Record
from ...schemas.record import ProcessRequest, ProcessResponse, TaskStatusResponse
from ...services import subscription_svc
from ...tasks.process_task import process_study_material
from ...tasks.celery_app import celery_app

router = APIRouter()


@router.post("/process/ask-ai")
async def ask_ai(req: dict, user: User = Depends(get_current_user)):
    """AI assistant: translate, explain, or summarize selected text."""
    prompt = req.get("prompt", "")
    if not prompt: raise HTTPException(400, "Prompt required")
    try:
        from ...services.ai_engine import _call_openai
        result = await _call_openai("You are a helpful study assistant. Answer concisely.", prompt, "deepseek-chat", 512)
        return {"result": result}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# Progress mapping: status → percentage
PROGRESS_MAP = {
    "queued": 5,
    "parsing": 20,
    "generating": 60,
    "exporting": 90,
    "completed": 100,
    "failed": 0,
}


@router.post("/process", response_model=ProcessResponse)
async def start_processing(
    req: ProcessRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _quota: User = Depends(require_quota),
):
    """Start AI processing for an uploaded file.

    Creates a record and enqueues a Celery task.
    The frontend should poll GET /process/{task_id}/status for progress.
    Requires remaining quota (trial or paid subscription).
    """
    # Verify file exists and belongs to user
    result = await db.execute(
        select(FileModel).where(
            FileModel.id == req.file_id,
            FileModel.user_id == current_user.id,
        )
    )
    file_obj = result.scalar_one_or_none()

    if not file_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file_obj.parse_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File parsing previously failed. Please re-upload.",
        )

    # Check for existing completed record for this file
    existing = await db.execute(
        select(Record).where(
            Record.file_id == req.file_id,
            Record.user_id == current_user.id,
            Record.status == "completed",
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This file has already been processed. Check your records.",
        )

    # Create record
    record = Record(
        user_id=current_user.id,
        file_id=req.file_id,
        title=file_obj.original_name,
        status="queued",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    # Consume quota (trial or subscription daily_used)
    # Skip in dev mode
    if settings.APP_ENV != "development":
        consumed = await subscription_svc.consume_quota(db, current_user)
        if not consumed:
            record.status = "failed"
            record.error_message = "Quota exhausted"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Quota exhausted. Please subscribe to continue.",
            )

    # Enqueue Celery task
    celery_task = process_study_material.delay(
        file_id=str(req.file_id),
        user_id=str(current_user.id),
        record_id=str(record.id),
        detail_level=req.detail_level,
        custom_notes=req.custom_notes,
    )

    return ProcessResponse(
        task_id=record.id,
        status="queued",
        message="Processing started",
    )


@router.get("/process/{task_id}/status", response_model=TaskStatusResponse)
async def get_processing_status(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Poll the status of an AI processing task.

    Returns the current status, progress percentage, and record_id when completed.
    """
    result = await db.execute(
        select(Record).where(
            Record.id == task_id,
            Record.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    progress = PROGRESS_MAP.get(record.status, 0)

    return TaskStatusResponse(
        task_id=record.id,
        status=record.status,
        progress=progress,
        record_id=record.id if record.status == "completed" else None,
        error_message=record.error_message if record.status == "failed" else None,
    )
