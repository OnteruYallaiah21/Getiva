from supabase import create_client, Client
from .config import settings
import os
from datetime import datetime


class SupabaseStorage:
    """Handle file storage operations with Supabase."""

    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name = settings.SUPABASE_BUCKET

    def upload_file(self, file_bytes: bytes, file_name: str, student_id: str) -> str:
        """Upload a file to Supabase storage.

        Args:
            file_bytes: File content as bytes
            file_name: Original file name
            student_id: Student ID for organizing files

        Returns:
            Public URL of the uploaded file
        """
        # Create unique file path
        timestamp = datetime.utcnow().isoformat()
        file_extension = os.path.splitext(file_name)[1]
        unique_name = f"{student_id}/{timestamp}{file_extension}"

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
            response = self.client.storage.from_(self.bucket_name).list(student_id)
            return response
        except Exception as e:
            print(f"Failed to list files: {str(e)}")
            return []


# Singleton instance
storage_client = SupabaseStorage()
