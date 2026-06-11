"""Fetch stored file bytes from B2 or public HTTP URLs (Supabase, etc.)."""

from __future__ import annotations

import logging
import mimetypes
import os
from typing import Optional, Tuple
from urllib.parse import unquote, urlparse

import httpx

logger = logging.getLogger(__name__)


def _filename_from_url(url: str) -> str:
    path = urlparse(url).path
    name = os.path.basename(unquote(path)) or "resume"
    return name


def _mime_for_name(name: str) -> str:
    mime, _ = mimetypes.guess_type(name)
    return mime or "application/octet-stream"


def parse_b2_location(stored_url: str) -> Optional[Tuple[str, str]]:
    """Return (bucket, key) from a B2 public or S3-style URL."""
    from .config import settings

    url = stored_url.strip()
    if "/file/" in url:
        rest = url.split("/file/", 1)[1]
        if "/" not in rest:
            return None
        bucket, key = rest.split("/", 1)
        return bucket, key

    endpoint = (settings.B2_ENDPOINT or "").strip().rstrip("/")
    bucket = (settings.B2_BUCKET or "").strip()
    if endpoint and bucket and url.startswith(f"{endpoint}/{bucket}/"):
        key = url[len(f"{endpoint}/{bucket}/") :]
        return bucket, key
    return None


def fetch_bytes_from_stored_url(stored_url: str) -> Tuple[bytes, str, str]:
    """Load file bytes from a stored URL. Returns (bytes, filename, content_type)."""
    url = (stored_url or "").strip()
    if not url:
        raise ValueError("No stored URL")

    filename = _filename_from_url(url)
    content_type = _mime_for_name(filename)

    b2_loc = parse_b2_location(url)
    if b2_loc:
        from . import b2_storage as b2

        if b2.b2_configured():
            bucket, key = b2_loc
            obj = b2._client().get_object(Bucket=bucket, Key=key)
            body = obj["Body"].read()
            ct = obj.get("ContentType") or content_type
            return body, filename, ct

    try:
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            ct = (resp.headers.get("content-type") or content_type).split(";")[0].strip()
            return resp.content, filename, ct
    except Exception as e:
        logger.error("Failed to fetch stored URL %s: %s", url, e)
        raise
