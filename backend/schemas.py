from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .models import UserRole, ApplicationStatus, PaymentStatus


# ============================================
# Auth Schemas
# ============================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.STUDENT
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[UUID] = None
    role: Optional[UserRole] = None


# ============================================
# User Schemas
# ============================================

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


# ============================================
# Student Schemas
# ============================================

class StudentCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class StudentResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    phone: Optional[str]
    resume_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StudentDetailResponse(StudentResponse):
    applications: List["ApplicationResponse"] = []


# ============================================
# Recruiter Schemas
# ============================================

class RecruiterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None


class RecruiterUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class RecruiterResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Application Schemas
# ============================================

class ApplicationCreate(BaseModel):
    student_id: UUID
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: UUID
    student_id: UUID
    recruiter_id: UUID
    company_name: str
    job_title: str
    status: ApplicationStatus
    applied_date: datetime
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    student: Optional[StudentResponse] = None
    recruiter: Optional[RecruiterResponse] = None
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    resume_url: Optional[str] = None


class ApplicationListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[ApplicationResponse]


# ============================================
# Payment Schemas
# ============================================

class StudentPaymentCreate(BaseModel):
    student_id: UUID
    amount: float = Field(..., gt=0)
    payment_type: str
    notes: Optional[str] = None


class StudentPaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class StudentPaymentResponse(BaseModel):
    id: UUID
    student_id: UUID
    amount: float
    payment_type: str
    status: PaymentStatus
    notes: Optional[str]
    payment_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class RecruiterPaymentCreate(BaseModel):
    recruiter_id: UUID
    amount: float = Field(..., gt=0)
    salary_month: str  # YYYY-MM format
    notes: Optional[str] = None


class RecruiterPaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class RecruiterPaymentResponse(BaseModel):
    id: UUID
    recruiter_id: UUID
    amount: float
    salary_month: str
    status: PaymentStatus
    notes: Optional[str]
    payment_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[StudentPaymentResponse]


# ============================================
# Analytics Schemas
# ============================================

class ApplicationStats(BaseModel):
    total_applications: int
    applied_count: int
    interview_count: int
    offer_count: int
    rejected_count: int
    success_rate: float


class RecruiterStats(BaseModel):
    recruiter_id: UUID
    recruiter_name: str
    total_applications: int
    applications_this_month: int
    success_rate: float


class DailyReport(BaseModel):
    date: datetime
    total_applications: int
    new_applications: int
    interviews_scheduled: int
    offers_received: int


class RecruiterPerformanceReport(BaseModel):
    total_recruiters: int
    recruiters: List[RecruiterStats]


class FinancialReport(BaseModel):
    total_revenue: float
    total_paid: float
    net_profit: float
    student_payments_count: int
    recruiter_payments_count: int


class SystemAnalytics(BaseModel):
    total_students: int
    total_recruiters: int
    total_applications: int
    total_revenue: float
    application_stats: ApplicationStats
    financial_report: FinancialReport


# Update forward references
StudentDetailResponse.update_forward_refs()
