#!/usr/bin/env python3
"""
First-time database setup: create all app tables (Neon) + first admin user.

Architecture:
  • Neon PostgreSQL — all app data (users, applications, …). Tables are created ONLY by
    Alembic migrations in this repo, not in the Supabase SQL editor.
  • Supabase — file storage only (Storage buckets for resumes / admin docs). You do not
    create app tables in Supabase.

Default admin (only when the users table is empty):
  username: getiva
  password: getiva@123   (override with GETIVA_SEED_PASSWORD)

Requires DATABASE_URL and SECRET_KEY in backend/.env, repo root .env, or the environment.

Usage:
  cd backend
  python scripts/seed_neon_admin.py

If the database already has users, this script skips creating an admin; run
  python scripts/ensure_getiva_admin.py
to create or reset the `getiva` admin.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# backend/ directory (parent of scripts/)
BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Install python-dotenv: pip install python-dotenv", file=sys.stderr)
        sys.exit(1)
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(BACKEND_DIR / ".env", override=True)
    if not os.environ.get("DATABASE_URL"):
        print(
            "ERROR: DATABASE_URL is not set. Add it to backend/.env or the repo root .env.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not os.environ.get("SECRET_KEY"):
        print(
            "ERROR: SECRET_KEY is not set. Add it to backend/.env or the repo root .env.",
            file=sys.stderr,
        )
        sys.exit(1)


def run_alembic_upgrade() -> None:
    """Apply all Alembic revisions to Neon."""
    print("Running: python -m alembic upgrade head …")
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(BACKEND_DIR),
        env=os.environ.copy(),
    )
    if r.returncode != 0:
        print("Alembic failed. Fix DATABASE_URL / migrations and retry.", file=sys.stderr)
        sys.exit(r.returncode)
    print("Migrations applied.")


def print_supabase_first_time_setup() -> None:
    """Explain Supabase Storage setup (no SQL tables for this app)."""
    bucket = os.environ.get("SUPABASE_BUCKET", "getiva_resume")
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_API_KEY") or ""
    configured = url and "example" not in url and key and not key.startswith("your_")

    print("— Supabase (file storage only) —")
    print("  App tables live in Neon, not Supabase. In Supabase you only need Storage.")
    print("  1) Create a project at https://supabase.com")
    print("  2) Storage → New bucket → name it exactly:", repr(bucket), "(or set SUPABASE_BUCKET in .env)")
    print("  3) Project Settings → API: copy Project URL → SUPABASE_URL")
    print("  4) Use the anon key or service role key → SUPABASE_KEY (or SUPABASE_API_KEY)")
    print("  5) Put those values in backend/.env (or repo root .env) and restart the API.")
    if not configured:
        print(f"  → Env check: Supabase not fully set — uploads will fail until URL/key/bucket are ready.")
    else:
        print(f"  → Env check: SUPABASE_URL/key look set; confirm bucket {bucket!r} exists under Storage.")


def seed_admin_if_empty() -> bool:
    sys.path.insert(0, str(REPO_ROOT))
    os.chdir(BACKEND_DIR)

    from backend.models import User, UserRole
    from backend.database import SessionLocal
    from backend.auth import hash_password

    username = os.environ.get("GETIVA_SEED_USERNAME", "getiva")
    email = os.environ.get("GETIVA_SEED_EMAIL", "getiva@getiva.local")
    password = os.environ.get("GETIVA_SEED_PASSWORD", "getiva@123")

    db = SessionLocal()
    try:
        n = db.query(User).count()
        if n > 0:
            print(f"Database already has {n} user(s). Skipping admin seed (bootstrap only when empty).")
            return False

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=1,
            is_temp_password=False,
        )
        db.add(user)
        db.commit()
        print("Created first admin user:")
        print(f"  Username: {username}")
        print(f"  Email:    {email}")
        print(f"  Password: {password}")
        print("  (Override defaults with GETIVA_SEED_USERNAME, GETIVA_SEED_EMAIL, GETIVA_SEED_PASSWORD.)")
        return True
    finally:
        db.close()


def main() -> None:
    print("GETIVA first-time DB setup — Neon tables (Alembic) + optional first admin\n")
    _load_env()
    run_alembic_upgrade()
    print()
    print_supabase_first_time_setup()
    print()
    created = seed_admin_if_empty()
    if created is False:
        print(
            "To create or reset the `getiva` admin (default password getiva@123), run:\n"
            "  python scripts/ensure_getiva_admin.py\n"
        )


if __name__ == "__main__":
    main()
