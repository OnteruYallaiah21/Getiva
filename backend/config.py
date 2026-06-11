from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    _backend_dir = Path(__file__).resolve().parent
    model_config = SettingsConfigDict(
        env_file=(_backend_dir.parent / ".env", _backend_dir / ".env"),
        case_sensitive=True,
        extra="ignore",
    )

    # App Configuration
    APP_NAME: str = "GETIVA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    # Open default browser to the app URL on server start (disable in production / CI)
    OPEN_BROWSER: bool = True

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Supabase (optional for development)
    SUPABASE_URL: str = "https://example.supabase.co"
    # Backend Storage uploads: prefer service_role JWT (server-only; bypasses Storage RLS when needed).
    # Legacy anon JWT — fallback if service role unset (local dev).
    # Do not use sb_publishable_* / sb_secret_* strings; use eyJ… JWTs from Dashboard → API.
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_KEY: str = "your_supabase_key"
    SUPABASE_API_KEY: str | None = None
    SUPABASE_BUCKET: str = "getiva_resume"
    SUPABASE_STORAGE_TIMEOUT_SECONDS: int = 60
    SUPABASE_UPLOAD_RETRIES: int = 2

    # Google Drive (optional): JSON is server-side only. Default path is backend/service_account.json
    # (resolved relative to the backend package, not the process cwd).
    GOOGLE_SERVICE_ACCOUNT_JSON_PATH: str = Field(
        default="service_account.json",
        description="Service account JSON path; relative to backend/ unless absolute.",
    )
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    # If false, never call Drive API (use Supabase only) even when service_account.json exists.
    GOOGLE_DRIVE_ENABLED: bool = False

    # Backblaze B2 (S3-compatible) — primary blob storage for recruiter resume uploads
    B2_ENABLED: bool = True
    B2_ENDPOINT: str = ""
    B2_KEY_ID: str = ""
    B2_APPLICATION_KEY: str = ""
    B2_BUCKET: str = ""
    B2_REGION: str = "us-east-005"
    # Friendly public URL base, e.g. https://f005.backblazeb2.com (for public buckets)
    B2_PUBLIC_BASE_URL: str = ""

    # CORS — include both localhost and 127.0.0.1 (browsers treat them as different origins)
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,http://localhost:8000,"
        "http://127.0.0.1:8000,http://127.0.0.1:3000"
    )

    # Email (optional — for future notifications; Gmail: use App Password, no spaces)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_USER", "SMTP_USERNAME", "smtp_username"),
    )
    SMTP_PASSWORD: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_PASSWORD", "smtp_password"),
    )

    @property
    def get_allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()

# If user supplied SUPABASE_API_KEY in env (older .env), copy it into SUPABASE_KEY
if getattr(settings, "SUPABASE_API_KEY", None):
    # Only overwrite default if SUPABASE_KEY is left as placeholder or empty
    if not settings.SUPABASE_KEY or settings.SUPABASE_KEY.startswith("your_"):
        settings.SUPABASE_KEY = settings.SUPABASE_API_KEY
