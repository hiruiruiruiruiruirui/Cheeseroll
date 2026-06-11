"""Tencent COS (Cloud Object Storage) client wrapper."""

import io
from datetime import datetime, timedelta, timezone

from ..config import settings

try:
    from qcloud_cos import CosConfig, CosS3Client
    _COS_AVAILABLE = True
except ImportError:
    CosConfig = None  # type: ignore
    CosS3Client = None  # type: ignore
    _COS_AVAILABLE = False


def get_cos_client():
    """Create and return a configured COS client."""
    if not _COS_AVAILABLE:
        raise RuntimeError("COS SDK not installed. Install cos-python-sdk-v5.")
    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY,
    )
    return CosS3Client(config)


def generate_cos_key(user_id: str, filename: str, prefix: str = "uploads") -> str:
    """Generate a unique COS object key.

    Format: {prefix}/{user_id}/{timestamp}_{filename}
    """
    from uuid import uuid4
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}/{user_id}/{ts}_{uuid4().hex[:8]}_{filename}"


async def upload_to_cos(
    client: CosS3Client,
    file_data: bytes,
    cos_key: str,
    content_type: str | None = None,
) -> str:
    """Upload file bytes to COS and return the object URL."""
    kwargs = {
        "Bucket": settings.COS_BUCKET,
        "Key": cos_key,
        "Body": io.BytesIO(file_data),
    }
    if content_type:
        kwargs["ContentType"] = content_type

    client.put_object(**kwargs)
    return f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{cos_key}"


async def delete_from_cos(client: CosS3Client, cos_key: str) -> None:
    """Delete an object from COS."""
    client.delete_object(
        Bucket=settings.COS_BUCKET,
        Key=cos_key,
    )


async def get_presigned_url(
    client: CosS3Client,
    cos_key: str,
    expire_seconds: int = 3600,
    download_name: str | None = None,
) -> str:
    """Generate a presigned download URL.

    Args:
        client: COS client instance.
        cos_key: Object key in COS.
        expire_seconds: URL validity duration.
        download_name: If set, Content-Disposition header will force download with this filename.
    """
    params = {}
    if download_name:
        encoded_name = download_name.encode("utf-8").decode("latin-1", errors="replace")
        params["response-content-disposition"] = f'attachment; filename="{encoded_name}"'

    url = client.get_presigned_url(
        Method="GET",
        Bucket=settings.COS_BUCKET,
        Key=cos_key,
        Expired=expire_seconds,
        Params=params if params else None,
    )
    return url
