from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from uuid import UUID

from database import get_db
from models import (
    Application, User, UserRole, Student, Recruiter, StudentPayment, RecruiterPayment,
    ApplicationStatus, PaymentStatus
)
from schemas import (
    ApplicationStats, RecruiterStats, DailyReport, RecruiterPerformanceReport,
    FinancialReport, SystemAnalytics
)
from routes.auth import get_current_user, require_role

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/applications", response_model=ApplicationStats)
def get_application_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """Get application statistics."""
    query = db.query(Application)

    # Filter by recruiter if not admin
    if current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
        query = query.filter(Application.recruiter_id == recruiter.id)

    total = query.count()
    applied_count = query.filter(Application.status == ApplicationStatus.APPLIED).count()
    interview_count = query.filter(Application.status == ApplicationStatus.INTERVIEW).count()
    offer_count = query.filter(Application.status == ApplicationStatus.OFFER).count()
    rejected_count = query.filter(Application.status == ApplicationStatus.REJECTED).count()

    success_rate = (offer_count / total * 100) if total > 0 else 0

    return {
        "total_applications": total,
        "applied_count": applied_count,
        "interview_count": interview_count,
        "offer_count": offer_count,
        "rejected_count": rejected_count,
        "success_rate": round(success_rate, 2),
    }


@router.get("/recruiters", response_model=RecruiterPerformanceReport)
def get_recruiter_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get recruiter performance metrics."""
    recruiters = db.query(Recruiter).all()
    recruiter_stats = []

    for recruiter in recruiters:
        total_apps = db.query(Application).filter(Application.recruiter_id == recruiter.id).count()
        this_month = (
            db.query(Application)
            .filter(
                Application.recruiter_id == recruiter.id,
                Application.created_at >= datetime.utcnow() - timedelta(days=30),
            )
            .count()
        )
        offers = (
            db.query(Application)
            .filter(
                Application.recruiter_id == recruiter.id,
                Application.status == ApplicationStatus.OFFER,
            )
            .count()
        )

        success_rate = (offers / total_apps * 100) if total_apps > 0 else 0

        recruiter_stats.append(
            RecruiterStats(
                recruiter_id=recruiter.id,
                recruiter_name=recruiter.name,
                total_applications=total_apps,
                applications_this_month=this_month,
                success_rate=round(success_rate, 2),
            )
        )

    return {
        "total_recruiters": len(recruiter_stats),
        "recruiters": recruiter_stats,
    }


@router.get("/daily", response_model=list[DailyReport])
def get_daily_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get daily application report."""
    reports = []
    today = datetime.utcnow()

    for i in range(days):
        date = today - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)

        total_apps = (
            db.query(func.count(Application.id))
            .filter(Application.created_at >= date_start, Application.created_at < date_end)
            .scalar()
        )

        new_apps = (
            db.query(func.count(Application.id))
            .filter(Application.created_at >= date_start, Application.created_at < date_end, Application.status == ApplicationStatus.APPLIED)
            .scalar()
        )

        interviews = (
            db.query(func.count(Application.id))
            .filter(Application.created_at >= date_start, Application.created_at < date_end, Application.status == ApplicationStatus.INTERVIEW)
            .scalar()
        )

        offers = (
            db.query(func.count(Application.id))
            .filter(Application.created_at >= date_start, Application.created_at < date_end, Application.status == ApplicationStatus.OFFER)
            .scalar()
        )

        reports.append(
            DailyReport(
                date=date,
                total_applications=total_apps,
                new_applications=new_apps,
                interviews_scheduled=interviews,
                offers_received=offers,
            )
        )

    return reports


@router.get("/financial", response_model=FinancialReport)
def get_financial_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get financial report."""
    # Student payments
    student_revenue = db.query(func.sum(StudentPayment.amount)).filter(
        StudentPayment.status == PaymentStatus.COMPLETED
    ).scalar() or 0

    student_payments_count = db.query(func.count(StudentPayment.id)).filter(
        StudentPayment.status == PaymentStatus.COMPLETED
    ).scalar()

    # Recruiter payments
    recruiter_paid = db.query(func.sum(RecruiterPayment.amount)).filter(
        RecruiterPayment.status == PaymentStatus.COMPLETED
    ).scalar() or 0

    recruiter_payments_count = db.query(func.count(RecruiterPayment.id)).filter(
        RecruiterPayment.status == PaymentStatus.COMPLETED
    ).scalar()

    net_profit = float(student_revenue) - float(recruiter_paid)

    return {
        "total_revenue": float(student_revenue),
        "total_paid": float(recruiter_paid),
        "net_profit": net_profit,
        "student_payments_count": student_payments_count,
        "recruiter_payments_count": recruiter_payments_count,
    }


@router.get("/system", response_model=SystemAnalytics)
def get_system_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get comprehensive system analytics."""
    # Count entities
    total_students = db.query(func.count(Student.id)).scalar()
    total_recruiters = db.query(func.count(Recruiter.id)).scalar()
    total_applications = db.query(func.count(Application.id)).scalar()

    # Application stats
    applied_count = db.query(func.count(Application.id)).filter(
        Application.status == ApplicationStatus.APPLIED
    ).scalar()
    interview_count = db.query(func.count(Application.id)).filter(
        Application.status == ApplicationStatus.INTERVIEW
    ).scalar()
    offer_count = db.query(func.count(Application.id)).filter(
        Application.status == ApplicationStatus.OFFER
    ).scalar()
    rejected_count = db.query(func.count(Application.id)).filter(
        Application.status == ApplicationStatus.REJECTED
    ).scalar()

    success_rate = (offer_count / total_applications * 100) if total_applications > 0 else 0

    application_stats = ApplicationStats(
        total_applications=total_applications,
        applied_count=applied_count,
        interview_count=interview_count,
        offer_count=offer_count,
        rejected_count=rejected_count,
        success_rate=round(success_rate, 2),
    )

    # Financial stats
    student_revenue = db.query(func.sum(StudentPayment.amount)).filter(
        StudentPayment.status == PaymentStatus.COMPLETED
    ).scalar() or 0

    recruiter_paid = db.query(func.sum(RecruiterPayment.amount)).filter(
        RecruiterPayment.status == PaymentStatus.COMPLETED
    ).scalar() or 0

    total_revenue = float(student_revenue)
    net_profit = total_revenue - float(recruiter_paid)

    financial_report = FinancialReport(
        total_revenue=total_revenue,
        total_paid=float(recruiter_paid),
        net_profit=net_profit,
        student_payments_count=db.query(func.count(StudentPayment.id)).filter(
            StudentPayment.status == PaymentStatus.COMPLETED
        ).scalar(),
        recruiter_payments_count=db.query(func.count(RecruiterPayment.id)).filter(
            RecruiterPayment.status == PaymentStatus.COMPLETED
        ).scalar(),
    )

    return {
        "total_students": total_students,
        "total_recruiters": total_recruiters,
        "total_applications": total_applications,
        "total_revenue": total_revenue,
        "application_stats": application_stats,
        "financial_report": financial_report,
    }


@router.get("/recruiter/{recruiter_id}/stats", response_model=RecruiterStats)
def get_recruiter_stats(
    recruiter_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get stats for a specific recruiter."""
    # Check permissions
    recruiter = db.query(Recruiter).filter(Recruiter.id == recruiter_id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    if current_user.role == UserRole.RECRUITER:
        current_recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
        if current_recruiter.id != recruiter_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    total_apps = db.query(func.count(Application.id)).filter(
        Application.recruiter_id == recruiter_id
    ).scalar()

    this_month = db.query(func.count(Application.id)).filter(
        Application.recruiter_id == recruiter_id,
        Application.created_at >= datetime.utcnow() - timedelta(days=30),
    ).scalar()

    offers = db.query(func.count(Application.id)).filter(
        Application.recruiter_id == recruiter_id,
        Application.status == ApplicationStatus.OFFER,
    ).scalar()

    success_rate = (offers / total_apps * 100) if total_apps > 0 else 0

    return RecruiterStats(
        recruiter_id=recruiter.id,
        recruiter_name=recruiter.name,
        total_applications=total_apps,
        applications_this_month=this_month,
        success_rate=round(success_rate, 2),
    )
