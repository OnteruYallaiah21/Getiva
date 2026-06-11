from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .models import UserRole, ApplicationStatus, PaymentStatus


# ============================================
# Auth Schemas
# ============================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.STUDENT
    full_name: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_as_none(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return v

    @field_validator("full_name", mode="before")
    @classmethod
    def empty_full_name_as_none(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return v.strip() if isinstance(v, str) else v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(Token):
    """Login payload: token plus first-login / forced password-change flag."""

    must_change_password: bool = False


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[UUID] = None
    role: Optional[UserRole] = None
    must_change_password: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class AdminResetPasswordRequest(BaseModel):
    """Admin sets a new password for any account (stored as hash; previous password is not recoverable)."""

    new_password: str = Field(..., min_length=8)


# ============================================
# User Schemas
# ============================================

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole
    is_active: int
    is_temp_password: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    per_page: int


class StoredDocumentResponse(BaseModel):
    """Supabase file URL stored in Postgres (e.g. Neon)."""

    id: UUID
    file_name: str
    title: Optional[str]
    storage_url: str
    uploaded_by_id: UUID
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


class StudentDirectoryEntry(BaseModel):
    """Student row for recruiter/admin pickers (links Student profile to login username)."""

    id: UUID
    username: str
    full_name: str
    email: str


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
    """``student_id`` may be omitted when exactly one active student exists (recruiter convenience)."""

    student_id: Optional[UUID] = None
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    job_description: str = Field(..., min_length=1)
    job_url: Optional[str] = None
    notes: Optional[str] = None
    resume_url: Optional[str] = None


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
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    resume_url: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    student: Optional[StudentResponse] = None
    recruiter: Optional[RecruiterResponse] = None


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


class StudentPaymentListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[StudentPaymentResponse]


class RecruiterPaymentListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[RecruiterPaymentResponse]


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
