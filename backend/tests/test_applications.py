"""Tests for applications endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Student, Recruiter, Application, ApplicationStatus, UserRole
from schemas import ApplicationCreate


class TestCreateApplication:
    """Tests for creating applications."""

    def test_create_application_recruiter(
        self,
        client: TestClient,
        db: Session,
        recruiter_auth_headers: dict,
        create_test_user,
    ):
        """Test recruiter creating an application."""
        recruiter_user = create_test_user(role=UserRole.RECRUITER)
        recruiter = Recruiter(user_id=recruiter_user.id, name="John Recruiter")
        db.add(recruiter)

        student_user = create_test_user(
            username="student", email="student@example.com", role=UserRole.STUDENT
        )
        student = Student(user_id=student_user.id, full_name="Jane Student")
        db.add(student)
        db.commit()

        app_data = {
            "student_id": str(student.id),
            "company_name": "TechCorp",
            "job_title": "Software Engineer",
            "job_description": "Build amazing software",
            "job_url": "https://example.com/job",
        }

        response = client.post(
            "/api/applications",
            json=app_data,
            headers=recruiter_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["company_name"] == app_data["company_name"]
        assert data["job_title"] == app_data["job_title"]
        assert data["status"] == ApplicationStatus.APPLIED.value

    def test_create_application_student_forbidden(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict,
        create_test_user,
    ):
        """Test that students cannot create applications."""
        student_user = create_test_user()
        student = Student(user_id=student_user.id, full_name="Jane Student")
        db.add(student)
        db.commit()

        app_data = {
            "student_id": str(student.id),
            "company_name": "TechCorp",
            "job_title": "Software Engineer",
        }

        response = client.post(
            "/api/applications",
            json=app_data,
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_create_application_missing_fields(
        self, client: TestClient, recruiter_auth_headers: dict
    ):
        """Test creating application with missing required fields."""
        response = client.post(
            "/api/applications",
            json={"company_name": "TechCorp"},
            headers=recruiter_auth_headers,
        )
        assert response.status_code == 422


class TestListApplications:
    """Tests for listing applications."""

    def test_list_applications_student(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict,
        create_test_user,
    ):
        """Test student viewing their applications."""
        student_user = create_test_user()
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

        # Create applications
        app1 = Application(
            student_id=student.id,
            recruiter_id=recruiter.id,
            company_name="TechCorp",
            job_title="Engineer",
        )
        db.add(app1)
        db.commit()

        response = client.get("/api/applications", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["company_name"] == "TechCorp"

    def test_list_applications_recruiter(
        self,
        client: TestClient,
        db: Session,
        recruiter_auth_headers: dict,
        create_test_user,
    ):
        """Test recruiter viewing their applications."""
        recruiter_user = create_test_user(role=UserRole.RECRUITER)
        recruiter = Recruiter(user_id=recruiter_user.id, name="John Recruiter")
        db.add(recruiter)

        student_user = create_test_user(
            username="student", email="student@example.com", role=UserRole.STUDENT
        )
        student = Student(user_id=student_user.id, full_name="Jane Student")
        db.add(student)
        db.commit()

        app1 = Application(
            student_id=student.id,
            recruiter_id=recruiter.id,
            company_name="TechCorp",
            job_title="Engineer",
        )
        db.add(app1)
        db.commit()

        response = client.get("/api/applications", headers=recruiter_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_applications_pagination(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict,
        create_test_user,
    ):
        """Test pagination of applications list."""
        student_user = create_test_user()
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

        # Create multiple applications
        for i in range(15):
            app = Application(
                student_id=student.id,
                recruiter_id=recruiter.id,
                company_name=f"Company{i}",
                job_title="Engineer",
            )
            db.add(app)
        db.commit()

        response = client.get(
            "/api/applications?skip=0&limit=10", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10


class TestUpdateApplication:
    """Tests for updating applications."""

    def test_update_application_status(
        self,
        client: TestClient,
        db: Session,
        recruiter_auth_headers: dict,
        create_test_user,
    ):
        """Test updating application status."""
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

        response = client.patch(
            f"/api/applications/{app.id}",
            json={"status": ApplicationStatus.INTERVIEW.value},
            headers=recruiter_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == ApplicationStatus.INTERVIEW.value

    def test_update_application_nonexistent(
        self,
        client: TestClient,
        recruiter_auth_headers: dict,
    ):
        """Test updating nonexistent application."""
        import uuid

        response = client.patch(
            f"/api/applications/{uuid.uuid4()}",
            json={"status": ApplicationStatus.INTERVIEW.value},
            headers=recruiter_auth_headers,
        )
        assert response.status_code == 404

    def test_update_application_unauthorized(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict,
        create_test_user,
    ):
        """Test student cannot update application."""
        recruiter_user = create_test_user(
            username="recruiter",
            email="recruiter@example.com",
            role=UserRole.RECRUITER,
        )
        recruiter = Recruiter(user_id=recruiter_user.id, name="John Recruiter")
        db.add(recruiter)

        student_user = create_test_user(role=UserRole.STUDENT)
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

        response = client.patch(
            f"/api/applications/{app.id}",
            json={"status": ApplicationStatus.INTERVIEW.value},
            headers=auth_headers,
        )
        assert response.status_code == 403


class TestDeleteApplication:
    """Tests for deleting applications."""

    def test_delete_application(
        self,
        client: TestClient,
        db: Session,
        recruiter_auth_headers: dict,
        create_test_user,
    ):
        """Test deleting an application."""
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

        response = client.delete(
            f"/api/applications/{app.id}",
            headers=recruiter_auth_headers,
        )
        assert response.status_code == 204

        # Verify deletion
        response = client.get(
            f"/api/applications/{app.id}",
            headers=recruiter_auth_headers,
        )
        assert response.status_code == 404
