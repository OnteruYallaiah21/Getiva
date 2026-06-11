#!/usr/bin/env python3
"""Smoke test: application resume view/download API endpoints.

Usage (repo root, venv active):
  export GETIVA_TEST_TOKEN="<jwt from login>"
  export APPLICATION_ID="<application uuid>"
  python backend/scripts/test_resume_endpoints.py

Or pass args:
  python backend/scripts/test_resume_endpoints.py --token ... --application-id ...
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


def _load_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(BACKEND_DIR / ".env")
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass


def main() -> int:
    _load_env()
    parser = argparse.ArgumentParser(description="Test resume view/download endpoints")
    parser.add_argument("--base-url", default=os.environ.get("GETIVA_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--token", default=os.environ.get("GETIVA_TEST_TOKEN", ""))
    parser.add_argument("--application-id", default=os.environ.get("APPLICATION_ID", ""))
    args = parser.parse_args()

    token = (args.token or "").strip()
    app_id = (args.application_id or "").strip()
    if not token or not app_id:
        print("Set GETIVA_TEST_TOKEN and APPLICATION_ID (or pass --token / --application-id)", file=sys.stderr)
        return 1

    base = args.base_url.rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}

    view_url = f"{base}/api/files/application/{app_id}/resume/view"
    download_url = f"{base}/api/files/application/{app_id}/resume/download"

    print("GET view:", view_url)
    with httpx.Client(timeout=60.0) as client:
        vr = client.get(view_url, headers=headers)
        print("view status:", vr.status_code, vr.headers.get("content-type"))
        if vr.status_code != 200:
            print(vr.text[:500], file=sys.stderr)
            return 1
        print("view bytes:", len(vr.content))

        print("GET download:", download_url)
        dr = client.get(download_url, headers=headers)
        print("download status:", dr.status_code, dr.headers.get("content-disposition"))
        if dr.status_code != 200:
            print(dr.text[:500], file=sys.stderr)
            return 1
        print("download bytes:", len(dr.content))

    print("OK — view and download endpoints work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
