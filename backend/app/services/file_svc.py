"""File service — handles upload validation, COS/local storage, and cleanup."""

import os
import uuid
import shutil
from datetime import datetime, timedelta, timezone

from ..config import settings
from ..utils.cos_client import (
    get_cos_client,
    generate_cos_key,
    upload_to_cos,
    delete_from_cos,
    get_presigned_url,
    _COS_AVAILABLE,
)

# Local storage directory for development (when COS is not configured)
_LOCAL_STORAGE = os.path.join(os.path.dirname(__file__), "..", "..", "local_storage")


def _use_cos() -> bool:
    """Check if COS is configured and available."""
    return _COS_AVAILABLE and settings.COS_SECRET_ID and settings.COS_SECRET_ID not in (
        "your-cos-secret-id", ""
    )


def validate_file(filename: str, file_size: int) -> tuple[str, str | None]:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in settings.ALLOWED_EXTENSIONS:
        return "", f"不支持的文件格式：.{ext}。支持格式：{', '.join(settings.ALLOWED_EXTENSIONS)}"

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        return "", f"文件过大：{file_size / 1024 / 1024:.1f}MB。最大支持 {settings.MAX_UPLOAD_SIZE_MB}MB"

    if file_size == 0:
        return "", "文件为空"

    return ext, None


async def upload_file(
    user_id: uuid.UUID,
    filename: str,
    file_data: bytes,
    content_type: str | None = None,
) -> dict:
    file_type, error = validate_file(filename, len(file_data))
    if error:
        raise ValueError(error)

    if _use_cos():
        # Upload to Tencent COS
        client = get_cos_client()
        cos_key = generate_cos_key(str(user_id), filename)
        await upload_to_cos(client, file_data, cos_key, content_type)
        return {
            "cos_key": cos_key,
            "file_type": file_type,
            "file_size_bytes": len(file_data),
        }
    else:
        # Save locally for development
        os.makedirs(_LOCAL_STORAGE, exist_ok=True)
        local_name = f"{uuid.uuid4().hex}_{filename}"
        local_path = os.path.join(_LOCAL_STORAGE, local_name)
        with open(local_path, "wb") as f:
            f.write(file_data)
        return {
            "cos_key": local_path,  # store local path in cos_key field for dev
            "file_type": file_type,
            "file_size_bytes": len(file_data),
        }


async def get_download_url(cos_key: str, download_name: str | None = None) -> str:
    if _use_cos():
        client = get_cos_client()
        return await get_presigned_url(client, cos_key, download_name=download_name)
    else:
        # For local storage, return a file:// URL or local path
        if os.path.exists(cos_key):
            return f"file://{cos_key}"
        raise FileNotFoundError(f"File not found: {cos_key}")


async def cleanup_file(cos_key: str) -> None:
    if _use_cos():
        client = get_cos_client()
        await delete_from_cos(client, cos_key)
    else:
        if os.path.exists(cos_key):
            os.unlink(cos_key)


async def save_temp_file(file_data: bytes, filename: str) -> str:
    import tempfile
    ext = os.path.splitext(filename)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(file_data)
    tmp.close()
    return tmp.name


def remove_temp_file(file_path: str) -> None:
    try:
        os.unlink(file_path)
    except OSError:
        pass
