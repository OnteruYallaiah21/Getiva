#!/usr/bin/env python3
"""
Reconcile a broken Alembic state with the real database (dev / recovery).

If you ran `stamp head` (or stamped too far ahead) while Postgres was still missing
columns or tables, Alembic will not run upgrades and the app will fail with errors
like `column users.is_temp_password does not exist`.

This script:
  1) `alembic stamp base` — clear the version row so migrations can run again
  2) `alembic upgrade head` — apply revisions; 001–003 are idempotent (skip existing
     tables / add missing columns)

No data is wiped. If you prefer a clean database, use Neon SQL:
  DROP SCHEMA public CASCADE; CREATE SCHEMA public;
then run `python scripts/seed_neon_admin.py`.

  cd backend
  python scripts/repair_migrations.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


def _run(args: list[str]) -> int:
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=str(BACKEND_DIR),
        env=os.environ.copy(),
    ).returncode


def main() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("pip install python-dotenv", file=sys.stderr)
        sys.exit(1)

    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(BACKEND_DIR / ".env", override=True)
    if not os.environ.get("DATABASE_URL"):
        print(
            "ERROR: DATABASE_URL not set (backend/.env or repo root .env).",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Step 1/2: alembic stamp base (forget recorded revision; no table drops) …")
    if _run(["stamp", "base"]) != 0:
        sys.exit(1)
    print("Step 2/2: alembic upgrade head (idempotent migrations) …")
    if _run(["upgrade", "head"]) != 0:
        sys.exit(1)
    print("Done. Schema should match models. Run: python scripts/seed_neon_admin.py")


if __name__ == "__main__":
    main()
