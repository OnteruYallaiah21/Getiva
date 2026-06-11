"""Backblaze B2 uploads via the S3-compatible API (server-side only)."""

from __future__ import annotations

import logging
import mimetypes
import os
import uuid
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

_s3_client: Optional[Any] = None


def b2_configured() -> bool:
    from .config import settings

    if not settings.B2_ENABLED:
        return False
    return bool(
        (settings.B2_ENDPOINT or "").strip()
        and (settings.B2_KEY_ID or "").strip()
        and (settings.B2_APPLICATION_KEY or "").strip()
        and (settings.B2_BUCKET or "").strip()
    )


def _client():
    global _s3_client
    if _s3_client is not None:
        return _s3_client
    import boto3

    from .config import settings

    _s3_client = boto3.client(
        "s3",
        endpoint_url=settings.B2_ENDPOINT.strip(),
        aws_access_key_id=settings.B2_KEY_ID.strip(),
        aws_secret_access_key=settings.B2_APPLICATION_KEY.strip(),
        region_name=settings.B2_REGION,
    )
    return _s3_client


def _public_url(bucket: str, key: str) -> str:
    """Public bucket URL (B2 friendly download URL)."""
    from .config import settings

    base = (settings.B2_PUBLIC_BASE_URL or "").strip().rstrip("/")
    if base:
        return f"{base}/file/{bucket}/{key}"
    endpoint = settings.B2_ENDPOINT.strip().rstrip("/")
    return f"{endpoint}/{bucket}/{key}"


def upload_bytes_to_b2(file_bytes: bytes, file_name: str, logical_prefix: str) -> str:
    """Upload bytes under ``logical_prefix/`` in the configured bucket; return a public URL."""
    from .config import settings

    bucket = settings.B2_BUCKET.strip()
    safe = os.path.basename(file_name) or "file.bin"
    prefix = logical_prefix.strip("/").replace("\\", "/")
    now = datetime.utcnow()
    # Readable UTC stamp in filename, e.g. 2026-06-11_14-30-22 (6/11/2026 when shown in UI)
    stamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    unique = f"{stamp}_{uuid.uuid4().hex[:8]}_{safe}"
    key = f"{prefix}/{unique}" if prefix else unique
    mime, _ = mimetypes.guess_type(safe)
    mime = mime or "application/octet-stream"

    _client().put_object(
        Bucket=bucket,
        Key=key,
        Body=file_bytes,
        ContentType=mime,
    )
    url = _public_url(bucket, key)
    logger.info("B2 upload ok bucket=%s key=%s", bucket, key)
    return url
