from .config import settings
import os
import uuid
import time
from datetime import datetime
from typing import Optional, Any
import httpx


class SupabaseStorage:
    """Handle file storage operations with Supabase."""

    def __init__(self):
        # Do NOT create the Supabase client at import time. Keep client None
        # until a storage operation requires it. This avoids crashing the app
        # during startup when credentials are missing/invalid.
        self.client: Optional[Any] = None
        self.bucket_name = settings.SUPABASE_BUCKET
        self.url = settings.SUPABASE_URL

    def _ensure_client(self):
        """Create the Supabase client on first use and validate configuration.

        Import the supabase package here to avoid module-level import errors
        when the package isn't installed in some environments.
        """
        if self.client is not None:
            return

        def _norm_jwt(v: Optional[str]) -> str:
            if not v:
                return ""
            return v.strip().replace("\n", "").replace("\r", "").replace(" ", "")

        url = (getattr(settings, "SUPABASE_URL", None) or "").strip().rstrip("/")
        service_role = _norm_jwt(getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None))
        anon = _norm_jwt(getattr(settings, "SUPABASE_KEY", None))

        # Prefer service_role for backend-only uploads; URLs are still saved in Postgres and exposed as links to the UI.
        if service_role and not service_role.startswith("your_"):
            key = service_role
            key_source = "SUPABASE_SERVICE_ROLE_KEY"
        elif anon and not anon.startswith("your_"):
            key = anon
            key_source = "SUPABASE_KEY"
        else:
            raise RuntimeError(
                "Supabase not configured: set SUPABASE_URL and either "
                "SUPABASE_SERVICE_ROLE_KEY (recommended for backend uploads) or SUPABASE_KEY (anon JWT)."
            )

        if not url or url.startswith("https://example"):
            raise RuntimeError(
                "Supabase not configured: set SUPABASE_URL in the environment or .env"
            )

        if key.startswith("sb_publishable_") or key.startswith("sb_secret_"):
            raise RuntimeError(
                f"{key_source} must be a legacy JWT (eyJ… three parts) from Supabase Dashboard → API. "
                "Do not use sb_publishable_* or sb_secret_* with this Python client."
            )

        try:
            # Local import so missing package doesn't break imports elsewhere
            from supabase import create_client
            from supabase.lib.client_options import ClientOptions

            timeout = max(5, int(getattr(settings, "SUPABASE_STORAGE_TIMEOUT_SECONDS", 60)))
            options = ClientOptions(
                postgrest_client_timeout=timeout,
                storage_client_timeout=timeout,
            )
            self.client = create_client(url, key, options=options)
        except Exception as e:
            msg = str(e)
            if "Invalid API key" in msg or "invalid" in msg.lower():
                raise RuntimeError(
                    f"Failed to create Supabase client: {msg}. "
                    f"Check SUPABASE_URL and {key_source} (JWT, no line breaks)."
                ) from e
            raise RuntimeError(f"Failed to create Supabase client: {e}") from e

    def _upload_with_retries(self, path: str, file_bytes: bytes):
        retries = max(0, int(getattr(settings, "SUPABASE_UPLOAD_RETRIES", 2)))
        for attempt in range(retries + 1):
            try:
                return self.client.storage.from_(self.bucket_name).upload(
                    path,
                    file_bytes,
                    {"cacheControl": "3600", "upsert": "false"},
                )
            except Exception as e:
                is_timeout = isinstance(e, httpx.ReadTimeout) or "timed out" in str(e).lower()
                if is_timeout and attempt < retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise

    def upload_file(self, file_bytes: bytes, file_name: str, student_id: str) -> str:
        """Upload a file to Supabase storage.

        Args:
            file_bytes: File content as bytes
            file_name: Original file name
            student_id: Student ID for organizing files

        Returns:
            Public URL of the uploaded file
        """
        # Ensure client exists before performing any operations
        self._ensure_client()

        # Create unique file path
        timestamp = datetime.utcnow().isoformat()
        file_extension = os.path.splitext(file_name)[1]
        unique_name = f"{student_id}/{timestamp}{file_extension}"

        # Ensure client exists before performing any operations
        self._ensure_client()

        try:
            # Upload file
            response = self._upload_with_retries(unique_name, file_bytes)

            # Generate public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(unique_name)

            return public_url
        except Exception as e:
            msg = str(e)
            if "Bucket not found" in msg:
                raise Exception(
                    f"Failed to upload file: bucket '{self.bucket_name}' not found in project {self.url}. "
                    "Create the bucket in Supabase Storage or set SUPABASE_BUCKET correctly."
                )
            raise Exception(f"Failed to upload file: {msg}")

    def upload_admin_document(self, file_bytes: bytes, file_name: str) -> str:
        """Upload an admin document to Supabase under admin-docs/; returns public URL."""
        self._ensure_client()
        safe_base = os.path.basename(file_name) or "document"
        file_extension = os.path.splitext(safe_base)[1]
        unique_name = f"admin-docs/{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:12]}{file_extension}"
        try:
            self._upload_with_retries(unique_name, file_bytes)
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(unique_name)
            return public_url
        except Exception as e:
            msg = str(e)
            if "Bucket not found" in msg:
                raise Exception(
                    f"Failed to upload admin document: bucket '{self.bucket_name}' not found in project {self.url}. "
                    "Create the bucket in Supabase Storage or set SUPABASE_BUCKET correctly."
                )
            raise Exception(f"Failed to upload admin document: {msg}")

    def delete_file(self, file_url: str):
        """Delete a file from Supabase storage.

        Args:
            file_url: Public URL of the file to delete
        """
        try:
            self._ensure_client()

            # Extract path from URL
            # URL format: https://bucket.supabase.co/storage/v1/object/public/bucket_name/path
            path = file_url.split(f"/{self.bucket_name}/")[1] if f"/{self.bucket_name}/" in file_url else None

            if path:
                self.client.storage.from_(self.bucket_name).remove([path])
        except Exception as e:
            print(f"Failed to delete file: {str(e)}")

    def list_files(self, student_id: str):
        """List all files for a student.

        Args:
            student_id: Student ID to list files for

        Returns:
            List of files metadata
        """
        try:
            self._ensure_client()
            response = self.client.storage.from_(self.bucket_name).list(student_id)
            return response
        except Exception as e:
            print(f"Failed to list files: {str(e)}")
            return []


# Singleton instance (lazy initialization)
storage_client = SupabaseStorage()
