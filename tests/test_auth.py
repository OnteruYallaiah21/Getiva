"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from models import UserRole


class TestRegister:
    """Tests for user registration."""

    def test_register_student_success(self, client: TestClient, test_user_data: dict):
        """Test successful student registration."""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == UserRole.STUDENT.value
        assert "password_hash" not in data

    def test_register_recruiter_success(self, client: TestClient, test_recruiter_data: dict):
        """Test successful recruiter registration."""
        response = client.post("/api/auth/register", json=test_recruiter_data)
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == UserRole.RECRUITER.value

    def test_register_admin_success(self, client: TestClient, test_admin_data: dict):
        """Test successful admin registration."""
        response = client.post("/api/auth/register", json=test_admin_data)
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == UserRole.ADMIN.value

    def test_register_duplicate_username(self, client: TestClient, test_user_data: dict):
        """Test registration with duplicate username."""
        client.post("/api/auth/register", json=test_user_data)
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client: TestClient, test_user_data: dict):
        """Test registration with duplicate email."""
        client.post("/api/auth/register", json=test_user_data)
        data = test_user_data.copy()
        data["username"] = "different_user"
        response = client.post("/api/auth/register", json=data)
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient, test_user_data: dict):
        """Test registration with invalid email."""
        data = test_user_data.copy()
        data["email"] = "invalid-email"
        response = client.post("/api/auth/register", json=data)
        assert response.status_code == 422

    def test_register_missing_required_field(self, client: TestClient):
        """Test registration with missing required fields."""
        response = client.post("/api/auth/register", json={"username": "test"})
        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""

    def test_login_success(self, client: TestClient, test_user_data: dict):
        """Test successful login."""
        client.post("/api/auth/register", json=test_user_data)
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

    def test_login_invalid_username(self, client: TestClient, test_user_data: dict):
        """Test login with invalid username."""
        client.post("/api/auth/register", json=test_user_data)
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": test_user_data["password"]},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client: TestClient, test_user_data: dict):
        """Test login with invalid password."""
        client.post("/api/auth/register", json=test_user_data)
        response = client.post(
            "/api/auth/login",
            json={"username": test_user_data["username"], "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_inactive_user(self, client: TestClient, test_user_data: dict, db):
        """Test login with inactive user."""
        from models import User
        from auth import hash_password

        user = User(
            username=test_user_data["username"],
            email=test_user_data["email"],
            password_hash=hash_password(test_user_data["password"]),
            role=test_user_data["role"],
            is_active=0,
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
        assert response.status_code == 401


class TestRefreshToken:
    """Tests for token refresh."""

    def test_refresh_token_success(self, client: TestClient, test_user_data: dict):
        """Test successful token refresh."""
        client.post("/api/auth/register", json=test_user_data)
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
        """Test refresh token with invalid token."""
        response = client.post(
            "/api/auth/refresh-token",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_refresh_token_missing_token(self, client: TestClient):
        """Test refresh token without token."""
        response = client.post("/api/auth/refresh-token")
        assert response.status_code == 403


class TestLogout:
    """Tests for user logout."""

    def test_logout_success(self, client: TestClient, auth_headers: dict):
        """Test successful logout."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200

    def test_logout_without_token(self, client: TestClient):
        """Test logout without token."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 403


class TestPasswordValidation:
    """Tests for password validation."""

    def test_weak_password(self, client: TestClient, test_user_data: dict):
        """Test registration with weak password."""
        data = test_user_data.copy()
        data["password"] = "weak"
        response = client.post("/api/auth/register", json=data)
        assert response.status_code == 422
