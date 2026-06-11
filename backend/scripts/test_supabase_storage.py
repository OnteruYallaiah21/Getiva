#!/usr/bin/env python3
"""Smoke-test Supabase Storage using the same settings as the API.

Run from the **backend** directory so `.env` is picked up:

    cd backend
    python scripts/test_supabase_storage.py

Requires: SUPABASE_URL, SUPABASE_BUCKET; and either SUPABASE_SERVICE_ROLE_KEY (preferred) or SUPABASE_KEY (anon JWT) in `backend/.env`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# backend/ as cwd for pydantic-settings `.env`
BACKEND_DIR = Path(__file__).resolve().parents[1]
os.chdir(BACKEND_DIR)
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR.parent))

from dotenv import load_dotenv

load_dotenv(BACKEND_DIR / ".env")

from backend.storage import storage_client  # noqa: E402
from backend.config import settings  # noqa: E402


def main() -> int:
    print("SUPABASE_URL:", (settings.SUPABASE_URL or "")[:48] + ("…" if len(settings.SUPABASE_URL or "") > 48 else ""))
    print("SUPABASE_BUCKET:", settings.SUPABASE_BUCKET)
    sr = (settings.SUPABASE_SERVICE_ROLE_KEY or "").strip()
    anon = (settings.SUPABASE_KEY or "").strip()
    if sr and not sr.startswith("your_"):
        print("Storage client will use: SUPABASE_SERVICE_ROLE_KEY (backend upload)")
        print("Key preview:", f"{sr[:12]}…{sr[-8:]} (len={len(sr)})")
    elif anon and not anon.startswith("your_"):
        print("Storage client will use: SUPABASE_KEY (anon fallback)")
        print("Key preview:", f"{anon[:12]}…{anon[-8:]} (len={len(anon)})")
    else:
        print("SUPABASE_SERVICE_ROLE_KEY / SUPABASE_KEY: (missing or placeholder)")

    if (settings.SUPABASE_URL or "").startswith("https://example"):
        print("\nERROR: Configure SUPABASE_URL in backend/.env first.")
        return 1
    if (not sr or sr.startswith("your_")) and (not anon or anon.startswith("your_")):
        print("\nERROR: Set SUPABASE_SERVICE_ROLE_KEY and/or SUPABASE_KEY in backend/.env.")
        return 1

    smoke_student = "00000000-0000-0000-0000-000000000001"
    content = b"GETIVA Supabase storage smoke test\n"
    name = "smoke-test.txt"

    print("\nUploading test object to bucket …")
    try:
        url = storage_client.upload_file(content, name, smoke_student)
        print("OK — public URL returned:")
        print(url)
        print("\nOpen the URL in a browser (bucket must be public or use signed URLs).")
        print("In Supabase: Storage →", settings.SUPABASE_BUCKET, "→ folder", smoke_student[:8] + "…")
        return 0
    except Exception as e:
        print("FAILED:", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
