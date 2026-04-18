from supabase import create_client, Client
from .config import settings
import os
from datetime import datetime
from typing import Optional


class SupabaseStorage:
    """Handle file storage operations with Supabase."""

    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name = settings.SUPABASE_BUCKET
        self._initialized = False

    def _ensure_initialized(self):
        """Lazily initialize the Supabase client on first use."""
        if not self._initialized:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                self._initialized = True
            except Exception as e:
                raise Exception(f"Failed to initialize Supabase client: {str(e)}")

    def _ensure_client(self):
        """Create the Supabase client on first use and validate configuration."""
        if self.client is not None:
            return

        url = getattr(settings, "SUPABASE_URL", None)
        key = getattr(settings, "SUPABASE_KEY", None)

        if not url or not key or key.startswith("your_") or url.startswith("https://example"):
            raise RuntimeError(
                "Supabase not configured: set SUPABASE_URL and SUPABASE_KEY in the environment or .env"
            )

        try:
            self.client = create_client(url, key)
        except Exception as e:
            # Surface a clearer error for misconfigured/invalid keys
            raise RuntimeError(f"Failed to create Supabase client: {e}")

    def upload_file(self, file_bytes: bytes, file_name: str, student_id: str) -> str:
        """Upload a file to Supabase storage.

        Args:
            file_bytes: File content as bytes
            file_name: Original file name
            student_id: Student ID for organizing files

        Returns:
            Public URL of the uploaded file
        """
        self._ensure_initialized()

        # Create unique file path
        timestamp = datetime.utcnow().isoformat()
        file_extension = os.path.splitext(file_name)[1]
        unique_name = f"{student_id}/{timestamp}{file_extension}"

        # Ensure client exists before performing any operations
        self._ensure_client()

        try:
            # Upload file
            response = self.client.storage.from_(self.bucket_name).upload(
                unique_name,
                file_bytes,
                {"cacheControl": "3600", "upsert": "false"},
            )

            # Generate public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(unique_name)

            return public_url
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

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
        self._ensure_initialized()

        try:
            self._ensure_client()
            response = self.client.storage.from_(self.bucket_name).list(student_id)
            return response
        except Exception as e:
            print(f"Failed to list files: {str(e)}")
            return []


# Singleton instance (lazy initialization)
storage_client = SupabaseStorage()
