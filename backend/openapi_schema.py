"""OpenAPI/Swagger schema configuration for GETIVA API."""

from fastapi.openapi.utils import get_openapi
from .main import app

def custom_openapi():
    """Generate custom OpenAPI schema for Swagger documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="GETIVA API",
        version="1.0.0",
        description="""
        # GETIVA - Job Application Tracking Platform API

        Complete REST API for job application tracking and consultancy management.

        ## Authentication
        All protected endpoints require JWT token in Authorization header:
        ```
        Authorization: Bearer <your_jwt_token>
        ```

        ## User Roles
        - **ADMIN**: Full system access, user management, analytics
        - **RECRUITER**: Create and manage applications, view analytics
        - **STUDENT**: Track applications, upload documents, manage payments

        ## Key Features
        - User authentication with JWT
        - Role-based access control
        - Application tracking with status updates
        - Payment management
        - File uploads and storage
        - Analytics and reporting
        """,
        routes=app.routes,
        tags=[
            {
                "name": "auth",
                "description": "Authentication endpoints - Login, Register, Token Management"
            },
            {
                "name": "applications",
                "description": "Job Application Management - Create, Read, Update, Delete applications"
            },
            {
                "name": "payments",
                "description": "Payment Management - Student and Recruiter payment tracking"
            },
            {
                "name": "analytics",
                "description": "Analytics and Reporting - System statistics and insights"
            },
            {
                "name": "files",
                "description": "File Management - Resume and document uploads"
            },
            {
                "name": "students",
                "description": "Student directory for recruiters (list students for assignment)"
            },
        ]
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "images/getiva.png",
        "altText": "GETIVA Logo"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
