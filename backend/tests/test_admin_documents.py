"""Admin Supabase document upload: URL persisted in Neon (Postgres)."""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def _bootstrap_admin_token(client: TestClient, test_admin_data: dict) -> str:
    """Create first admin via bootstrap and return JWT."""
    r = client.post("/api/auth/bootstrap", json=test_admin_data)
    assert r.status_code == 201, r.text
    login = client.post(
        "/api/auth/login",
        json={
            "username": test_admin_data["username"],
            "password": test_admin_data["password"],
        },
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


class TestBootstrapAdminProfile:
    """Verify a single bootstrap admin can be created (Neon user row)."""

    def test_bootstrap_creates_admin_profile(self, client: TestClient, test_admin_data: dict):
        token = _bootstrap_admin_token(client, test_admin_data)
        me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200
        body = me.json()
        assert body["username"] == test_admin_data["username"]
        assert body["role"] == "admin"
        assert body["is_temp_password"] is False


class TestAdminDocumentsSupabaseNeon:
    """Upload uses Supabase (mocked); metadata + URL stored in DB."""

    @patch(
        "backend.file_storage_dispatch.storage_client.upload_admin_document",
        return_value="https://example.supabase.co/storage/v1/object/public/resumes/admin-docs/test.pdf",
    )
    def test_admin_upload_saves_url_in_database(
        self,
        _mock_upload: object,
        client: TestClient,
        test_admin_data: dict,
    ):
        token = _bootstrap_admin_token(client, test_admin_data)
        files = {"file": ("policy.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
        data = {"title": "HR Policy 2026"}
        res = client.post(
            "/api/files/admin/documents",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            data=data,
        )
        assert res.status_code == 201, res.text
        row = res.json()
        assert row["title"] == "HR Policy 2026"
        assert row["file_name"] == "policy.pdf"
        assert "supabase.co" in row["storage_url"]
        assert "admin-docs" in row["storage_url"]

        listed = client.get(
            "/api/files/admin/documents",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert listed.status_code == 200
        items = listed.json()
        assert len(items) == 1
        assert items[0]["id"] == row["id"]

    @patch("backend.file_storage_dispatch.storage_client.upload_admin_document", return_value="https://x.test/a.pdf")
    def test_non_admin_cannot_upload_admin_document(
        self,
        _mock_upload: object,
        client: TestClient,
        test_admin_data: dict,
        test_user_data: dict,
    ):
        admin_tok = _bootstrap_admin_token(client, test_admin_data)
        created = client.post(
            "/api/auth/users",
            json=test_user_data,
            headers={"Authorization": f"Bearer {admin_tok}"},
        )
        assert created.status_code == 201
        st = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        st_tok = st.json()["access_token"]
        files = {"file": ("x.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")}
        res = client.post(
            "/api/files/admin/documents",
            headers={"Authorization": f"Bearer {st_tok}"},
            files=files,
        )
        assert res.status_code == 403
