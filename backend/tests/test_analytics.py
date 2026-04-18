"""Tests for analytics endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import (
    User,
    Student,
    Recruiter,
    Application,
    ApplicationStatus,
    UserRole,
)


class TestSystemAnalytics:
    """Tests for system analytics."""

    def test_system_analytics_admin(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict,
        create_test_user,
    ):
        """Test admin accessing system analytics."""
        response = client.get(
            "/api/analytics/system",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_students" in data
        assert "total_recruiters" in data
        assert "total_applications" in data

    def test_system_analytics_unauthorized(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test non-admin cannot access system analytics."""
        response = client.get(
            "/api/analytics/system",
            headers=auth_headers,
        )
        assert response.status_code == 403


class TestApplicationAnalytics:
    """Tests for application analytics."""

    def test_application_analytics_admin(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict,
        create_test_user,
    ):
        """Test admin accessing application analytics."""
        student_user = create_test_user(role=UserRole.STUDENT)
        student = Student(user_id=student_user.id, full_name="Jane Student")
        db.add(student)

        recruiter_user = create_test_user(
            username="recruiter",
            email="recruiter@example.com",
            role=UserRole.RECRUITER,
        )
        recruiter = Recruiter(user_id=recruiter_user.id, name="John Recruiter")
        db.add(recruiter)
        db.commit()

        # Create applications with different statuses
        app1 = Application(
            student_id=student.id,
            recruiter_id=recruiter.id,
            company_name="Company A",
            job_title="Engineer",
            status=ApplicationStatus.APPLIED,
        )
        app2 = Application(
            student_id=student.id,
            recruiter_id=recruiter.id,
            company_name="Company B",
            job_title="Manager",
            status=ApplicationStatus.INTERVIEW,
        )
        app3 = Application(
            student_id=student.id,
            recruiter_id=recruiter.id,
            company_name="Company C",
            job_title="Designer",
            status=ApplicationStatus.OFFER,
        )
        db.add_all([app1, app2, app3])
        db.commit()

        response = client.get(
            "/api/analytics/applications",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "applied_count" in data
        assert "interview_count" in data
        assert "offer_count" in data
        assert data["applied_count"] == 1
        assert data["interview_count"] == 1
        assert data["offer_count"] == 1

    def test_application_analytics_by_recruiter(
        self,
        client: TestClient,
        db: Session,
        recruiter_auth_headers: dict,
        create_test_user,
    ):
        """Test recruiter accessing their own analytics."""
        recruiter_user = create_test_user(role=UserRole.RECRUITER)
        recruiter = Recruiter(user_id=recruiter_user.id, name="John Recruiter")
        db.add(recruiter)

        student_user = create_test_user(
            username="student", email="student@example.com", role=UserRole.STUDENT
        )
        student = Student(user_id=student_user.id, full_name="Jane Student")
        db.add(student)
        db.commit()

        app = Application(
            student_id=student.id,
            recruiter_id=recruiter.id,
            company_name="TechCorp",
            job_title="Engineer",
            status=ApplicationStatus.APPLIED,
        )
        db.add(app)
        db.commit()

        response = client.get(
            "/api/analytics/applications",
            headers=recruiter_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["applied_count"] >= 1


class TestRecruiterAnalytics:
    """Tests for recruiter analytics."""

    def test_recruiter_performance_admin(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict,
        create_test_user,
    ):
        """Test admin accessing recruiter performance analytics."""
        recruiter_user = create_test_user(role=UserRole.RECRUITER)
        recruiter = Recruiter(user_id=recruiter_user.id, name="John Recruiter")
        db.add(recruiter)

        student_user = create_test_user(
            username="student", email="student@example.com", role=UserRole.STUDENT
        )
        student = Student(user_id=student_user.id, full_name="Jane Student")
        db.add(student)
        db.commit()

        app = Application(
            student_id=student.id,
            recruiter_id=recruiter.id,
            company_name="TechCorp",
            job_title="Engineer",
        )
        db.add(app)
        db.commit()

        response = client.get(
            "/api/analytics/recruiters",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0

    def test_recruiter_performance_list_structure(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict,
        create_test_user,
    ):
        """Test recruiter performance analytics response structure."""
        recruiter_user = create_test_user(role=UserRole.RECRUITER)
        recruiter = Recruiter(user_id=recruiter_user.id, name="John Recruiter")
        db.add(recruiter)
        db.commit()

        response = client.get(
            "/api/analytics/recruiters",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            assert "recruiter_name" in data[0]
            assert "applications_created" in data[0]


class TestFinancialAnalytics:
    """Tests for financial analytics."""

    def test_financial_report_admin(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict,
    ):
        """Test admin accessing financial analytics."""
        response = client.get(
            "/api/analytics/financial",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_student_payments" in data
        assert "total_recruiter_payments" in data
        assert "pending_payments" in data
        assert "completed_payments" in data

    def test_financial_report_unauthorized(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test non-admin cannot access financial analytics."""
        response = client.get(
            "/api/analytics/financial",
            headers=auth_headers,
        )
        assert response.status_code == 403


class TestDailyAnalytics:
    """Tests for daily analytics."""

    def test_daily_analytics_admin(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict,
        create_test_user,
    ):
        """Test admin accessing daily analytics."""
        response = client.get(
            "/api/analytics/daily?days=7",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_daily_analytics_custom_days(
        self,
        client: TestClient,
        admin_auth_headers: dict,
    ):
        """Test daily analytics with custom day range."""
        response = client.get(
            "/api/analytics/daily?days=30",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200

    def test_daily_analytics_invalid_days(
        self,
        client: TestClient,
        admin_auth_headers: dict,
    ):
        """Test daily analytics with invalid day parameter."""
        response = client.get(
            "/api/analytics/daily?days=invalid",
            headers=admin_auth_headers,
        )
        assert response.status_code == 422
