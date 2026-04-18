from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Union
from uuid import UUID

from ..database import get_db
from ..models import (
    StudentPayment, RecruiterPayment, User, UserRole, Student, Recruiter, PaymentStatus
)
from ..schemas import (
    StudentPaymentCreate, StudentPaymentUpdate, StudentPaymentResponse,
    RecruiterPaymentCreate, RecruiterPaymentUpdate, RecruiterPaymentResponse,
    PaymentListResponse
)
from .auth import get_current_user, require_role

router = APIRouter(prefix="/api/payments", tags=["payments"])


# ============================================
# Student Payments
# ============================================

@router.post("/student", response_model=StudentPaymentResponse, status_code=201)
def create_student_payment(
    payment_data: StudentPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Create a student payment record."""
    # Verify student exists
    student = db.query(Student).filter(Student.id == payment_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db_payment = StudentPayment(
        student_id=payment_data.student_id,
        amount=payment_data.amount,
        payment_type=payment_data.payment_type,
        notes=payment_data.notes,
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


@router.get("/student", response_model=PaymentListResponse)
def list_student_payments(
    student_id: UUID = Query(None),
    status: PaymentStatus = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List student payments."""
    query = db.query(StudentPayment)

    # Role-based filtering
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        query = query.filter(StudentPayment.student_id == student.id)
    elif student_id:
        query = query.filter(StudentPayment.student_id == student_id)

    if status:
        query = query.filter(StudentPayment.status == status)

    total = query.count()
    payments = (
        query.order_by(desc(StudentPayment.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": payments,
    }


@router.get("/student/{payment_id}", response_model=StudentPaymentResponse)
def get_student_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student payment details."""
    payment = db.query(StudentPayment).filter(StudentPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Check permissions
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if payment.student_id != student.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return payment


@router.patch("/student/{payment_id}", response_model=StudentPaymentResponse)
def update_student_payment(
    payment_id: UUID,
    payment_update: StudentPaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Update student payment status."""
    payment = db.query(StudentPayment).filter(StudentPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment_update.status:
        payment.status = payment_update.status
    if payment_update.notes:
        payment.notes = payment_update.notes

    db.commit()
    db.refresh(payment)

    return payment


# ============================================
# Recruiter Payments
# ============================================

@router.post("/recruiter", response_model=RecruiterPaymentResponse, status_code=201)
def create_recruiter_payment(
    payment_data: RecruiterPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Create a recruiter payment record."""
    # Verify recruiter exists
    recruiter = db.query(Recruiter).filter(Recruiter.id == payment_data.recruiter_id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    db_payment = RecruiterPayment(
        recruiter_id=payment_data.recruiter_id,
        amount=payment_data.amount,
        salary_month=payment_data.salary_month,
        notes=payment_data.notes,
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


@router.get("/recruiter", response_model=PaymentListResponse)
def list_recruiter_payments(
    recruiter_id: UUID = Query(None),
    status: PaymentStatus = Query(None),
    salary_month: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List recruiter payments."""
    query = db.query(RecruiterPayment)

    # Role-based filtering
    if current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
        query = query.filter(RecruiterPayment.recruiter_id == recruiter.id)
    elif recruiter_id:
        query = query.filter(RecruiterPayment.recruiter_id == recruiter_id)

    if status:
        query = query.filter(RecruiterPayment.status == status)
    if salary_month:
        query = query.filter(RecruiterPayment.salary_month == salary_month)

    total = query.count()
    payments = (
        query.order_by(desc(RecruiterPayment.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": payments,
    }


@router.get("/recruiter/{payment_id}", response_model=RecruiterPaymentResponse)
def get_recruiter_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recruiter payment details."""
    payment = db.query(RecruiterPayment).filter(RecruiterPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Check permissions
    if current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
        if payment.recruiter_id != recruiter.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return payment


@router.patch("/recruiter/{payment_id}", response_model=RecruiterPaymentResponse)
def update_recruiter_payment(
    payment_id: UUID,
    payment_update: RecruiterPaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Update recruiter payment status."""
    payment = db.query(RecruiterPayment).filter(RecruiterPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment_update.status:
        payment.status = payment_update.status
    if payment_update.notes:
        payment.notes = payment_update.notes

    db.commit()
    db.refresh(payment)

    return payment
