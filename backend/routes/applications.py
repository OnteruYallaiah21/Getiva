from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Application, User, UserRole, Student, Recruiter, ApplicationStatus
from ..schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationDetailResponse, ApplicationListResponse
from .auth import get_current_user, require_role

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    app_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN)),
):
    """Create a new job application."""
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
    if not recruiter:
        raise HTTPException(
            status_code=403,
            detail="Recruiter profile not found. Applications must be created by an account with a recruiter profile.",
        )

    if app_data.student_id is None:
        active_students = (
            db.query(Student)
            .join(User, Student.user_id == User.id)
            .filter(User.role == UserRole.STUDENT, User.is_active == 1)
            .all()
        )
        if len(active_students) != 1:
            raise HTTPException(
                status_code=400,
                detail="student_id is required when more than one active student exists",
            )
        student = active_students[0]
        resolved_student_id = student.id
    else:
        student = db.query(Student).filter(Student.id == app_data.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        resolved_student_id = app_data.student_id

    job_title = (app_data.job_title or "").strip() or app_data.company_name

    db_application = Application(
        student_id=resolved_student_id,
        recruiter_id=recruiter.id,
        company_name=app_data.company_name,
        job_title=job_title,
        job_description=app_data.job_description,
        job_url=app_data.job_url,
        notes=app_data.notes,
        resume_url=app_data.resume_url,
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application


@router.get("", response_model=ApplicationListResponse)
def list_applications(
    student_id: UUID = Query(None),
    recruiter_id: UUID = Query(None),
    status: ApplicationStatus = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List applications with filtering."""
    query = db.query(Application)

    # Role-based filtering
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        query = query.filter(Application.student_id == student.id)
    elif current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
        query = query.filter(Application.recruiter_id == recruiter.id)

    # Additional filters
    if student_id:
        query = query.filter(Application.student_id == student_id)
    if recruiter_id:
        query = query.filter(Application.recruiter_id == recruiter_id)
    if status:
        query = query.filter(Application.status == status)

    # Pagination
    total = query.count()
    applications = query.order_by(desc(Application.created_at)).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": applications,
    }


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get application details."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check permissions
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if application.student_id != student.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
        if application.recruiter_id != recruiter.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return application


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID,
    app_update: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN)),
):
    """Update application status."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check permissions
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
    if recruiter and application.recruiter_id != recruiter.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    if app_update.status:
        application.status = app_update.status
    if app_update.notes:
        application.notes = app_update.notes

    db.commit()
    db.refresh(application)

    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN)),
):
    """Delete an application."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check permissions
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
    if recruiter and application.recruiter_id != recruiter.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(application)
    db.commit()
