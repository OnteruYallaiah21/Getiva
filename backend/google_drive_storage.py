"""Google Drive uploads using a service account JSON file (server-side only)."""

from __future__ import annotations

import io
import logging
import mimetypes
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_SCOPES = ("https://www.googleapis.com/auth/drive.file",)


def resolve_service_account_path() -> Optional[Path]:
    """Return path to service account JSON if the file exists.

    Default ``backend/service_account.json`` — same directory as this module (stable regardless of
    where you run ``uvicorn`` from). Override with ``GOOGLE_SERVICE_ACCOUNT_JSON_PATH`` (absolute or
    relative to ``backend/``).
    """
    from .config import settings

    raw = (settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH or "").strip()
    base = Path(__file__).resolve().parent  # backend/
    if not raw:
        p = base / "service_account.json"
    else:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = base / p
    return p if p.is_file() else None


def drive_configured() -> bool:
    return resolve_service_account_path() is not None


_google_imports_ok: bool | None = None


def google_imports_available() -> bool:
    """True if google-api-python-client and google-auth are importable (cached)."""
    global _google_imports_ok
    if _google_imports_ok is not None:
        return _google_imports_ok
    try:
        import google.oauth2.service_account  # noqa: F401
        import googleapiclient.discovery  # noqa: F401
        _google_imports_ok = True
    except ImportError:
        _google_imports_ok = False
    return _google_imports_ok


def drive_upload_eligible() -> bool:
    """Use Drive uploads only when enabled, JSON exists, and Google libs are installed."""
    from .config import settings

    if not settings.GOOGLE_DRIVE_ENABLED:
        return False
    if not resolve_service_account_path():
        return False
    return google_imports_available()


def _build_drive():
    path = resolve_service_account_path()
    if not path:
        raise FileNotFoundError("Google service account JSON not found")
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(str(path), scopes=_SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_bytes_to_google_drive(file_bytes: bytes, file_name: str, logical_folder: str) -> str:
    """Upload bytes to Drive; set anyone-reader; return a view URL.

    ``logical_folder`` is used in the Drive file name (e.g. student UUID or ``admin-docs``).
    Optional ``GOOGLE_DRIVE_FOLDER_ID`` in settings must be a folder shared with the service account.
    """
    from googleapiclient.http import MediaIoBaseUpload

    from .config import settings

    drive = _build_drive()
    safe = os.path.basename(file_name) or "file.bin"
    unique = f"{logical_folder}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:8]}_{safe}"
    mime, _ = mimetypes.guess_type(safe)
    mime = mime or "application/octet-stream"
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime, resumable=True)

    folder_id = (settings.GOOGLE_DRIVE_FOLDER_ID or "").strip()
    if not folder_id:
        raise RuntimeError(
            "GOOGLE_DRIVE_FOLDER_ID is required for service-account uploads. "
            "Use a folder inside a Shared Drive and share it with the service-account email."
        )
    body: dict = {"name": unique, "parents": [folder_id]}

    created = drive.files().create(
        body=body,
        media_body=media,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    file_id = created["id"]

    drive.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
        supportsAllDrives=True,
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"
