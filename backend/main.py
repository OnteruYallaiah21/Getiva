from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .routes import auth, applications, payments, analytics, files

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
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


# API v1 routes
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Include routers
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(payments.router)
app.include_router(analytics.router)
app.include_router(files.router)


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
