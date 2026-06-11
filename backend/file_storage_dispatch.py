"""Resume / document uploads: Backblaze B2 first, then Supabase fallback."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def upload_resume_bytes(file_bytes: bytes, file_name: str, student_id: str) -> str:
    """Upload resume bytes. Uses Backblaze B2 when configured; else Supabase."""
    from . import b2_storage as b2
    from .storage import storage_client

    if b2.b2_configured():
        try:
            return b2.upload_bytes_to_b2(file_bytes, file_name, f"resumes/{student_id}")
        except Exception as e:
            logger.warning("B2 resume upload failed, using Supabase: %s", e)

    try:
        return storage_client.upload_file(file_bytes, file_name, student_id)
    except Exception as e:
        logger.error("Supabase resume upload failed: %s", e, exc_info=True)
        raise


def upload_admin_document_bytes(file_bytes: bytes, file_name: str) -> str:
    """Admin policy docs: B2 first if configured, else Supabase."""
    from . import b2_storage as b2
    from .storage import storage_client

    if b2.b2_configured():
        try:
            return b2.upload_bytes_to_b2(file_bytes, file_name, "admin-docs")
        except Exception as e:
            logger.warning("B2 admin upload failed, using Supabase: %s", e)

    try:
        return storage_client.upload_admin_document(file_bytes, file_name)
    except Exception as e:
        logger.error("Supabase admin document upload failed: %s", e, exc_info=True)
        raise
