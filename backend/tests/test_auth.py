"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient

from models import UserRole


def _admin_headers(client: TestClient, test_admin_data: dict) -> dict:
    assert client.post("/api/auth/bootstrap", json=test_admin_data).status_code == 201
    r = client.post(
        "/api/auth/login",
        json={
            "username": test_admin_data["username"],
            "password": test_admin_data["password"],
        },
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


class TestBootstrap:
    """First admin creation."""

    def test_bootstrap_creates_admin(self, client: TestClient, test_admin_data: dict):
        response = client.post("/api/auth/bootstrap", json=test_admin_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_admin_data["username"]
        assert data["role"] == UserRole.ADMIN.value
        assert data["is_temp_password"] is False

    def test_bootstrap_rejected_when_users_exist(self, client: TestClient, test_admin_data: dict):
        client.post("/api/auth/bootstrap", json=test_admin_data)
        response = client.post("/api/auth/bootstrap", json=test_admin_data)
        assert response.status_code == 403

    def test_bootstrap_requires_admin_role(self, client: TestClient, test_user_data: dict):
        response = client.post("/api/auth/bootstrap", json=test_user_data)
        assert response.status_code == 400


class TestAdminCreatesUsers:
    """Admin-only user provisioning."""

    def test_admin_create_student(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        response = client.post("/api/auth/users", json=test_user_data, headers=h)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["role"] == UserRole.STUDENT.value
        assert data["is_temp_password"] is True

    def test_admin_create_recruiter(self, client: TestClient, test_admin_data: dict, test_recruiter_data: dict):
        h = _admin_headers(client, test_admin_data)
        response = client.post("/api/auth/users", json=test_recruiter_data, headers=h)
        assert response.status_code == 201
        assert response.json()["role"] == UserRole.RECRUITER.value

    def test_duplicate_username(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        client.post("/api/auth/users", json=test_user_data, headers=h)
        response = client.post("/api/auth/users", json=test_user_data, headers=h)
        assert response.status_code == 400

    def test_duplicate_email(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        client.post("/api/auth/users", json=test_user_data, headers=h)
        data = test_user_data.copy()
        data["username"] = "otheruser"
        response = client.post("/api/auth/users", json=data, headers=h)
        assert response.status_code == 400

    def test_invalid_email(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        data = test_user_data.copy()
        data["email"] = "invalid-email"
        response = client.post("/api/auth/users", json=data, headers=h)
        assert response.status_code == 422

    def test_create_student_without_full_name(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        data = test_user_data.copy()
        data["username"] = "noname_student"
        del data["full_name"]
        response = client.post("/api/auth/users", json=data, headers=h)
        assert response.status_code == 201
        assert response.json()["username"] == "noname_student"

    def test_create_user_without_email_gets_placeholder(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        data = {
            "username": "noemailuser",
            "password": test_user_data["password"],
            "role": UserRole.STUDENT.value,
            "full_name": "Has Name",
        }
        response = client.post("/api/auth/users", json=data, headers=h)
        assert response.status_code == 201
        assert response.json()["email"] == "noemailuser@users.getiva.local"

    def test_non_admin_cannot_create_user(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        assert client.post("/api/auth/users", json=test_user_data, headers=h).status_code == 201
        st_login = client.post(
            "/api/auth/login",
            json={"username": test_user_data["username"], "password": test_user_data["password"]},
        )
        assert st_login.status_code == 200
        st_headers = {"Authorization": f"Bearer {st_login.json()['access_token']}"}
        response = client.post(
            "/api/auth/users",
            json={
                "username": "another",
                "email": "another@example.com",
                "password": "TestPassword123!",
                "role": "student",
                "full_name": "Another",
            },
            headers=st_headers,
        )
        assert response.status_code == 403


class TestLogin:
    """Login and token payload."""

    def test_login_success(self, client: TestClient, test_user_data: dict, test_admin_data: dict):
        h = _admin_headers(client, test_admin_data)
        assert client.post("/api/auth/users", json=test_user_data, headers=h).status_code == 201
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["must_change_password"] is True

    def test_login_invalid_username(self, client: TestClient, test_user_data: dict, test_admin_data: dict):
        h = _admin_headers(client, test_admin_data)
        client.post("/api/auth/users", json=test_user_data, headers=h)
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": test_user_data["password"]},
        )
        assert response.status_code == 401

    def test_login_invalid_password(self, client: TestClient, test_user_data: dict, test_admin_data: dict):
        h = _admin_headers(client, test_admin_data)
        client.post("/api/auth/users", json=test_user_data, headers=h)
        response = client.post(
            "/api/auth/login",
            json={"username": test_user_data["username"], "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, client: TestClient, test_user_data: dict, db):
        from models import User
        from auth import hash_password

        user = User(
            username=test_user_data["username"],
            email=test_user_data["email"],
            password_hash=hash_password(test_user_data["password"]),
            role=UserRole(test_user_data["role"]),
            is_active=0,
            is_temp_password=False,
        )
        db.add(user)
        db.commit()

        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 403


class TestChangePassword:
    def test_change_password_clears_temp_flag(self, client: TestClient, test_user_data: dict, test_admin_data: dict):
        h = _admin_headers(client, test_admin_data)
        assert client.post("/api/auth/users", json=test_user_data, headers=h).status_code == 201
        login = client.post(
            "/api/auth/login",
            json={"username": test_user_data["username"], "password": test_user_data["password"]},
        )
        token = login.json()["access_token"]
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": test_user_data["password"],
                "new_password": "NewPassword456!",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["must_change_password"] is False
        again = client.post(
            "/api/auth/login",
            json={"username": test_user_data["username"], "password": "NewPassword456!"},
        )
        assert again.json()["must_change_password"] is False


class TestRefreshToken:
    """Token refresh."""

    def test_refresh_token_success(self, client: TestClient, test_user_data: dict, test_admin_data: dict):
        h = _admin_headers(client, test_admin_data)
        client.post("/api/auth/users", json=test_user_data, headers=h)
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        response = client.post(
            "/api/auth/refresh-token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid_token(self, client: TestClient):
        response = client.post(
            "/api/auth/refresh-token",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_refresh_token_missing_token(self, client: TestClient):
        response = client.post("/api/auth/refresh-token")
        assert response.status_code == 401


class TestLogout:
    """Logout."""

    def test_logout_success(self, client: TestClient, auth_headers: dict):
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200

    def test_logout_without_token(self, client: TestClient):
        response = client.post("/api/auth/logout")
        assert response.status_code == 200


class TestPasswordValidation:
    """Password rules on create."""

    def test_weak_password_on_create(self, client: TestClient, test_admin_data: dict, test_user_data: dict):
        h = _admin_headers(client, test_admin_data)
        data = test_user_data.copy()
        data["password"] = "weak"
        response = client.post("/api/auth/users", json=data, headers=h)
        assert response.status_code == 422

