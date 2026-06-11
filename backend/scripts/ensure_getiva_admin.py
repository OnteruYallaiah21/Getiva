#!/usr/bin/env python3
"""
Create or update the admin user `getiva` with password `getiva@123` (defaults).

Use when the DB already has other users (the empty-DB seed script skips) or you want
to reset this account.

Environment (optional overrides):
  GETIVA_ADMIN_USERNAME   default: getiva
  GETIVA_ADMIN_PASSWORD   default: getiva@123
  GETIVA_ADMIN_EMAIL      default: getiva@getiva.local (only used when creating new user)

Requires DATABASE_URL in environment, backend/.env, or the repo root .env (SECRET_KEY is only for the app).

Runs `alembic upgrade head` first so the schema matches the models (skip with GETIVA_SKIP_ALEMBIC=1).

Usage:
  cd backend
  python scripts/ensure_getiva_admin.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


def run_alembic_upgrade() -> None:
    """Apply migrations so ORM columns (e.g. users.is_temp_password) exist."""
    print("Applying database migrations (alembic upgrade head) …")
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(BACKEND_DIR),
        env=os.environ.copy(),
    )
    if r.returncode != 0:
        print("Alembic failed. Fix DATABASE_URL / migrations and retry.", file=sys.stderr)
        sys.exit(r.returncode)
    print("Migrations applied.")


def main() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("pip install python-dotenv", file=sys.stderr)
        sys.exit(1)

    load_dotenv(BACKEND_DIR / ".env")
    if not os.environ.get("DATABASE_URL"):
        load_dotenv(REPO_ROOT / ".env")
    if not os.environ.get("DATABASE_URL"):
        print(
            "ERROR: DATABASE_URL not set. Add it to backend/.env or the repo root .env, "
            "or export DATABASE_URL.",
            file=sys.stderr,
        )
        sys.exit(1)

    if os.environ.get("GETIVA_SKIP_ALEMBIC", "").strip().lower() not in ("1", "true", "yes"):
        run_alembic_upgrade()
        print()

    # Import as backend.* so models' package-relative imports (e.g. .database) resolve.
    sys.path.insert(0, str(REPO_ROOT))
    os.chdir(BACKEND_DIR)

    from sqlalchemy.orm import Session
    from backend.models import User, UserRole
    from backend.database import SessionLocal
    from backend.auth import hash_password

    username = os.environ.get("GETIVA_ADMIN_USERNAME", "getiva")
    password = os.environ.get("GETIVA_ADMIN_PASSWORD", "getiva@123")
    default_email = os.environ.get("GETIVA_ADMIN_EMAIL", "getiva@getiva.local")

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.password_hash = hash_password(password)
            user.role = UserRole.ADMIN
            user.is_active = 1
            user.is_temp_password = False
            db.commit()
            print(f"Updated existing user {username!r}: role=admin, password set, active.")
        else:
            if db.query(User).filter(User.email == default_email).first():
                print(
                    f"ERROR: email {default_email!r} is already taken. "
                    f"Set GETIVA_ADMIN_EMAIL to a free address.",
                    file=sys.stderr,
                )
                sys.exit(1)
            user = User(
                username=username,
                email=default_email,
                password_hash=hash_password(password),
                role=UserRole.ADMIN,
                is_active=1,
                is_temp_password=False,
            )
            db.add(user)
            db.commit()
            print(f"Created admin {username!r} with email {default_email!r}.")
        print(f"Sign in: username={username!r} password={password!r}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
