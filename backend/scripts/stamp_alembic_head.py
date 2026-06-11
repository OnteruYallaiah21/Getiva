#!/usr/bin/env python3
"""
Tell Alembic the database is already at `head` without running migration bodies.

Use when tables match the models but `alembic_version` is empty or behind (e.g. manual
SQL or a failed migration). After stamping, `alembic upgrade head` is a no-op.

  cd backend
  python scripts/stamp_alembic_head.py

Optional: stamp a specific revision instead of head:
  GETIVA_STAMP_REV=001 python scripts/stamp_alembic_head.py

If the database schema is already fully applied (same as `head`), stamp `head` only —
do not stamp an older revision or Alembic will try to run later upgrades again.

If you stamped `head` but the real database is missing columns (e.g. `is_temp_password`),
`alembic upgrade head` will do nothing. Run:

  python scripts/repair_migrations.py

That re-applies idempotent migrations without dropping data.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


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

    rev = os.environ.get("GETIVA_STAMP_REV", "head").strip() or "head"
    print(f"Stamping database to revision {rev!r} (no DDL will run) …")
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "stamp", rev],
        cwd=str(BACKEND_DIR),
        env=os.environ.copy(),
    )
    if r.returncode != 0:
        sys.exit(r.returncode)
    print("Done. Run `python scripts/seed_neon_admin.py` or `alembic upgrade head` next.")


if __name__ == "__main__":
    main()
