"""Pytest configuration and fixtures for GETIVA tests."""

import os

# Ensure SECRET_KEY exists if tests run without a .env (DATABASE_URL should come from .env / CI).
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .main import app
from .database import Base, get_db
from .models import User, UserRole
from .auth import hash_password


# Use SQLite in-memory database for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _disable_google_drive_in_tests(monkeypatch: pytest.MonkeyPatch):
    """So local service_account.json does not bypass Supabase mocks or call real Drive."""
    import backend.google_drive_storage as gds

    monkeypatch.setattr(gds, "resolve_service_account_path", lambda: None)


@pytest.fixture(autouse=True)
def _disable_b2_in_tests(monkeypatch: pytest.MonkeyPatch):
    """Tests mock Supabase; do not call real Backblaze B2 when backend/.env has keys."""
    import backend.b2_storage as b2

    monkeypatch.setattr(b2, "b2_configured", lambda: False)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a test database and session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """Create a test client with dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user_data() -> dict:
    """Sample user registration data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "role": UserRole.STUDENT.value,
        "full_name": "Test User",
    }


@pytest.fixture
def test_recruiter_data() -> dict:
    """Sample recruiter registration data."""
    return {
        "username": "recruiter",
        "email": "recruiter@example.com",
        "password": "RecruiterPass123!",
        "role": UserRole.RECRUITER.value,
        "full_name": "John Recruiter",
    }


@pytest.fixture
def test_admin_data() -> dict:
    """Sample admin registration data."""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "role": UserRole.ADMIN.value,
    }


@pytest.fixture
def create_test_user(db: Session):
    """Factory to create test users in database."""
    def _create_user(
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "TestPassword123!",
        role: UserRole = UserRole.STUDENT,
        is_active: int = 1,
    ) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
            is_temp_password=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _create_user


@pytest.fixture
def get_auth_token(client: TestClient, test_user_data: dict, test_admin_data: dict):
    """Get JWT for a user created by bootstrap admin (or the bootstrap admin)."""

    def _get_token(user_data: dict | None = None) -> str:
        data = user_data or test_user_data
        boot = client.post("/api/auth/bootstrap", json=test_admin_data)
        assert boot.status_code == 201, boot.text
        admin_login = client.post(
            "/api/auth/login",
            json={
                "username": test_admin_data["username"],
                "password": test_admin_data["password"],
            },
        )
        assert admin_login.status_code == 200, admin_login.text
        admin_tok = admin_login.json()["access_token"]
        if data["username"] == test_admin_data["username"]:
            return admin_tok
        created = client.post(
            "/api/auth/users",
            json=data,
            headers={"Authorization": f"Bearer {admin_tok}"},
        )
        assert created.status_code == 201, created.text
        login = client.post(
            "/api/auth/login",
            json={"username": data["username"], "password": data["password"]},
        )
        assert login.status_code == 200, login.text
        return login.json()["access_token"]

    return _get_token


@pytest.fixture
def auth_headers(get_auth_token: callable) -> dict:
    """Get authorization headers with valid token."""
    token = get_auth_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client: TestClient, test_admin_data: dict, get_auth_token: callable):
    """Get authorization headers for admin user."""
    token = get_auth_token(test_admin_data)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def recruiter_auth_headers(client: TestClient, test_recruiter_data: dict, get_auth_token: callable):
    """Get authorization headers for recruiter user."""
    token = get_auth_token(test_recruiter_data)
    return {"Authorization": f"Bearer {token}"}
