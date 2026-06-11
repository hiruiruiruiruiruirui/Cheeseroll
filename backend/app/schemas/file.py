"""File Pydantic schemas."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    file_id: uuid.UUID
    original_name: str
    file_type: str
    file_size_bytes: int
    parse_status: str
    message: str = "File uploaded successfully"


class FileRead(BaseModel):
    id: uuid.UUID
    original_name: str
    file_type: str
    file_size_bytes: int
    parse_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
