#!/usr/bin/env python3
"""Smoke test: connect to Backblaze B2 (S3-compatible API) and list buckets.

Install once:
  pip install boto3 python-dotenv

Set in backend/.env (or export):
  B2_ENDPOINT=https://s3.us-west-004.backblazeb2.com
  B2_KEY_ID=your_key_id
  B2_APPLICATION_KEY=your_application_key

Optional upload test:
  B2_BUCKET=your-bucket-name

Usage (from repo root, venv active):
  python backend/scripts/test_b2_connection.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(BACKEND_DIR / ".env")
    load_dotenv(REPO_ROOT / ".env")


def _validate_b2_key_id(key_id: str) -> list[str]:
    """Return human-readable issues with the access key id format."""
    issues: list[str] = []
    if len(key_id) < 20:
        issues.append(
            f"B2_KEY_ID is only {len(key_id)} chars; Backblaze Application Key IDs are usually ~24 chars "
            "(e.g. 004abc...000000004). You may have pasted account id or a truncated value."
        )
    if not key_id.startswith(("004", "005", "002", "003")):
        issues.append(
            "B2_KEY_ID should start with 004/005 (Application Key ID from App Keys page)."
        )
    return issues


def main() -> int:
    _load_env()

    endpoint = (os.environ.get("B2_ENDPOINT") or "").strip()
    key_id = (
        os.environ.get("B2_KEY_ID")
        or os.environ.get("keyID")
        or os.environ.get("AWS_ACCESS_KEY_ID")
        or ""
    ).strip().strip('"')
    app_key = (
        os.environ.get("B2_APPLICATION_KEY")
        or os.environ.get("applicationKey")
        or os.environ.get("AWS_SECRET_ACCESS_KEY")
        or ""
    ).strip().strip('"')
    bucket = (os.environ.get("B2_BUCKET") or "").strip()

    missing = [name for name, val in [
        ("B2_ENDPOINT", endpoint),
        ("B2_KEY_ID", key_id),
        ("B2_APPLICATION_KEY", app_key),
    ] if not val]
    if missing:
        print("Missing env vars:", ", ".join(missing), file=sys.stderr)
        print("Add them to backend/.env and retry.", file=sys.stderr)
        return 1

    for msg in _validate_b2_key_id(key_id):
        print("WARN:", msg, file=sys.stderr)
    print(
        "Note: Backblaze Master Application Keys do NOT work with the S3 API.\n"
        "      Create a new key at: Backblaze → App Keys → Add a New Application Key\n"
        "      Enable 'List All Bucket Names' if you need list_buckets.\n"
        "      Docs: https://www.backblaze.com/docs/cloud-storage-s3-compatible-app-keys",
        file=sys.stderr,
    )

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        print("Install boto3: pip install boto3", file=sys.stderr)
        return 1

    print("Connecting to B2 …")
    print("  endpoint:", endpoint)
    print("  key_id:", key_id[:6] + "…" + key_id[-4:] if len(key_id) > 12 else key_id)

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=app_key,
        region_name=os.environ.get("B2_REGION", "us-east-005"),
    )

    try:
        resp = s3.list_buckets()
    except (BotoCoreError, ClientError) as e:
        print("FAIL — list_buckets:", e, file=sys.stderr)
        return 1

    buckets = resp.get("Buckets") or []
    print("OK — list_buckets succeeded")
    if not buckets:
        print("  (no buckets in this account)")
    else:
        for b in buckets:
            print(f"  - {b.get('Name')}")

    if not bucket:
        print("\nOptional: set B2_BUCKET in .env to run a tiny upload test.")
        return 0

    test_key = "_getiva_smoke_test/hello.txt"
    body = b"GETIVA B2 connectivity test"
    print(f"\nUpload test → s3://{bucket}/{test_key}")
    try:
        s3.put_object(Bucket=bucket, Key=test_key, Body=body, ContentType="text/plain")
        head = s3.head_object(Bucket=bucket, Key=test_key)
        print("OK — upload + head_object")
        print("  size:", head.get("ContentLength"))
        s3.delete_object(Bucket=bucket, Key=test_key)
        print("OK — cleaned up test object")
    except (BotoCoreError, ClientError) as e:
        print("FAIL — upload test:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
