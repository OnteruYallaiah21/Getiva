"""Tests for main app endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check_success(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
        assert "environment" in data

    def test_health_check_response_structure(self, client: TestClient):
        """Test health check response structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        required_fields = ["status", "app", "version", "environment"]
        for field in required_fields:
            assert field in data


class TestRootEndpoint:
    """Tests for root and API info endpoints."""

    def test_root_serves_landing_html(self, client: TestClient):
        """Root serves the GETIVA landing page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "GETIVA" in response.text

    def test_api_info_json(self, client: TestClient):
        """API metadata JSON for programmatic clients."""
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["docs"] == "/docs"
        assert data["redoc"] == "/redoc"


class TestDocumentation:
    """Tests for API documentation."""

    def test_swagger_ui_available(self, client: TestClient):
        """Test Swagger UI is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self, client: TestClient):
        """Test ReDoc is available."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema_available(self, client: TestClient):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
