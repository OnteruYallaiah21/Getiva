import os
import sys
import threading
import webbrowser
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .routes import auth, applications, payments, analytics, files, students

# Frontend paths (project root / frontend — CSS/JS live beside public/)
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
FRONTEND_DIR = _PROJECT_ROOT / "frontend"
PUBLIC_DIR = FRONTEND_DIR / "public"


def _schedule_open_browser() -> None:
    """Open the landing page in the default browser after the server is listening."""
    if not settings.OPEN_BROWSER:
        return
    if os.environ.get("CI"):
        return
    # TestClient triggers lifespan; do not open a tab during pytest
    if "pytest" in sys.modules:
        return

    url = f"http://127.0.0.1:{settings.PORT}/"

    def _open() -> None:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Timer(1.25, _open).start()


# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    _schedule_open_browser()
    yield
    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Job Application Tracking & Consultancy Management System",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS: explicit origins from env + regex so localhost vs 127.0.0.1 and any dev port work
# (browsers treat them as different origins; OPTIONS preflight fails with 400 if Origin is not allowed).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
    allow_origin_regex=r"https?://(127\.0\.0\.1|localhost)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/info")
def api_info():
    """JSON metadata for API clients (landing page is served at `/`)."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Static assets (index.html uses /css/, /js/, /images/)
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
app.mount("/images", StaticFiles(directory=PUBLIC_DIR / "images"), name="images")


def _index_file_response() -> FileResponse:
    index = PUBLIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(
            status_code=500,
            detail="Frontend index missing (expected frontend/public/index.html)",
        )
    return FileResponse(index)


@app.get("/")
def root():
    """Serve the marketing landing page."""
    return _index_file_response()


@app.get("/index.html")
def index_html_alias():
    """Same as `/` (logout and links use index.html)."""
    return _index_file_response()


def _public_html(filename: str) -> FileResponse:
    path = PUBLIC_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(path)


@app.get("/admin-dashboard.html")
def admin_dashboard_page():
    """Admin dashboard UI."""
    return _public_html("admin-dashboard.html")


@app.get("/student-dashboard.html")
def student_dashboard_page():
    """Student dashboard UI."""
    return _public_html("student-dashboard.html")


@app.get("/recruiter-dashboard.html")
def recruiter_dashboard_page():
    """Recruiter dashboard UI."""
    return _public_html("recruiter-dashboard.html")


@app.get("/login.html")
def login_page():
    """Sign-in page (no self-registration)."""
    return _public_html("login.html")


@app.get("/change-password.html")
def change_password_page():
    """Forced password change after temporary password."""
    return _public_html("change-password.html")


def _project_root_file(filename: str) -> FileResponse:
    """Serve a file from the repository root (e.g. index-old.html, styles.css)."""
    path = _PROJECT_ROOT / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(path)


@app.get("/index-old.html")
def index_old_page():
    """Classic marketing landing page at repo root (embedded in admin preview)."""
    return _project_root_file("index-old.html")


@app.get("/landing-old.html")
def landing_old_page():
    """Alias for index-old.html (legacy admin links)."""
    return _project_root_file("index-old.html")


@app.get("/styles.css")
def legacy_landing_styles():
    """CSS for index-old.html (repo root styles.css)."""
    return _project_root_file("styles.css")


@app.get("/script.js")
def legacy_landing_script():
    """JS for index-old.html (frontend/js/script.js)."""
    path = FRONTEND_DIR / "js" / "script.js"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Script not found")
    return FileResponse(path)


# Include routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(applications.router)
app.include_router(payments.router)
app.include_router(analytics.router)
app.include_router(files.router)


# Custom OpenAPI schema for Swagger documentation
def custom_openapi():
    """Generate custom OpenAPI schema for Swagger documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="GETIVA API",
        version=settings.APP_VERSION,
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
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "/images/getiva.png",
        "altText": "GETIVA Logo",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    import traceback

    if settings.DEBUG:
        traceback.print_exc()

    return {
        "detail": str(exc) if settings.DEBUG else "Internal server error",
        "status_code": 500,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
