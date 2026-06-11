"""Record Pydantic schemas."""

import uuid
from datetime import datetime
from pydantic import BaseModel


class ProcessRequest(BaseModel):
    file_id: uuid.UUID
    detail_level: str = "default"  # brief | default | detailed
    custom_notes: str = ""


class ProcessResponse(BaseModel):
    task_id: uuid.UUID
    status: str
    message: str = "Processing started"


class TaskStatusResponse(BaseModel):
    task_id: uuid.UUID
    status: str  # queued | parsing | generating | exporting | completed | failed
    progress: int  # 0-100
    record_id: uuid.UUID | None = None
    error_message: str | None = None


class RecordCreate(BaseModel):
    file_id: uuid.UUID


class RecordRead(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    share_code: str | None = None
    folder_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordDetail(BaseModel):
    id: uuid.UUID
    title: str
    original_markdown: str | None = None
    status: str
    share_code: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecordListResponse(BaseModel):
    items: list[RecordRead]
    total: int
    page: int
    page_size: int


class PdfDownloadResponse(BaseModel):
    url: str
    expires_in: int = 3600  # presigned URL valid for 1 hour
