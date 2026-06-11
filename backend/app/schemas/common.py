"""Common Pydantic schemas for API responses."""

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class StatusResponse(BaseModel):
    status: str
    progress: int
    message: str | None = None
