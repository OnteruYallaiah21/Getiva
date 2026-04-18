# GETIVA Backend API

Modern FastAPI backend for the Job Application Tracking & Consultancy Management System.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database
- pip/poetry package manager

### Installation

1. **Clone and setup environment:**

```bash
cd getiva
cp .env.example .env
# Edit .env with your database credentials
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Create database tables:**

```bash
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

4. **Run development server:**

```bash
python main.py
# or
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication

```http
POST /api/auth/register         # Register new user
POST /api/auth/login            # Login and get token
POST /api/auth/logout           # Logout
POST /api/auth/refresh-token    # Refresh access token
```

**Example Login:**
```json
{
  "username": "john_doe",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Applications

```http
POST   /api/applications           # Create application
GET    /api/applications           # List applications
GET    /api/applications/{id}      # Get application details
PATCH  /api/applications/{id}      # Update status
DELETE /api/applications/{id}      # Delete application
```

**Query Filters:**
- `student_id`: Filter by student
- `recruiter_id`: Filter by recruiter
- `status`: Filter by status (applied, interview, offer, rejected, withdrawn)
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)

**Example Create Application:**
```json
{
  "student_id": "uuid-here",
  "company_name": "Google",
  "job_title": "Senior Engineer",
  "job_description": "We are looking for...",
  "job_url": "https://google.com/careers/...",
  "notes": "Strong candidate"
}
```

### Payments

#### Student Payments
```http
POST   /api/payments/student              # Create payment
GET    /api/payments/student              # List payments
GET    /api/payments/student/{id}         # Get payment details
PATCH  /api/payments/student/{id}         # Update payment
```

#### Recruiter Payments
```http
POST   /api/payments/recruiter            # Create payment
GET    /api/payments/recruiter            # List payments
GET    /api/payments/recruiter/{id}       # Get payment details
PATCH  /api/payments/recruiter/{id}       # Update payment
```

**Example Create Student Payment:**
```json
{
  "student_id": "uuid-here",
  "amount": 500.00,
  "payment_type": "service_fee",
  "notes": "Monthly subscription"
}
```

### Analytics

```http
GET /api/analytics/applications         # Application stats
GET /api/analytics/recruiters           # Recruiter performance
GET /api/analytics/daily                # Daily report
GET /api/analytics/financial            # Financial report
GET /api/analytics/system               # Complete system analytics
GET /api/analytics/recruiter/{id}/stats # Specific recruiter stats
```

**Example Response:**
```json
{
  "total_students": 150,
  "total_recruiters": 25,
  "total_applications": 4500,
  "total_revenue": 45230.00,
  "application_stats": {
    "total_applications": 4500,
    "applied_count": 3200,
    "interview_count": 800,
    "offer_count": 450,
    "rejected_count": 50,
    "success_rate": 10.0
  },
  "financial_report": {
    "total_revenue": 45230.00,
    "total_paid": 28450.00,
    "net_profit": 16780.00,
    "student_payments_count": 300,
    "recruiter_payments_count": 120
  }
}
```

## 🔐 Authentication

All protected endpoints require Bearer token in Authorization header:

```http
Authorization: Bearer <your_access_token>
```

**Token Expiration:** 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

## 👥 Role-Based Access Control

### Admin
- Full system access
- User management
- Payment management
- All analytics

### Recruiter
- Create applications for students
- View assigned applications
- View personal payments
- View personal performance stats

### Student
- View own applications
- View own payments
- Cannot create applications

## 🗄️ Database Schema

### Users
- id (UUID)
- username (unique)
- email (unique)
- password_hash
- role (admin, recruiter, student)
- is_active
- created_at, updated_at

### Students
- id (UUID)
- user_id (FK)
- full_name
- phone
- resume_url
- created_at, updated_at

### Recruiters
- id (UUID)
- user_id (FK)
- name
- phone
- created_at, updated_at

### Applications
- id (UUID)
- student_id (FK)
- recruiter_id (FK)
- company_name
- job_title
- status (applied, interview, offer, rejected, withdrawn)
- applied_date
- notes
- created_at, updated_at

### Student Payments
- id (UUID)
- student_id (FK)
- amount
- payment_type
- status (pending, completed, failed, refunded)
- created_at, updated_at

### Recruiter Payments
- id (UUID)
- recruiter_id (FK)
- amount
- salary_month
- status (pending, completed, failed, refunded)
- created_at, updated_at

## 🔧 Configuration

Edit `.env` to configure:

```env
# Database
DATABASE_URL=postgresql://user:password@host/getiva

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase (for file storage)
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_API_KEY=your_key
SUPABASE_BUCKET=resumes

# Application
ENVIRONMENT=development
DEBUG=False
PORT=8000
```

## 📊 Performance Optimization

- **Connection Pooling**: Configured with `pool_size=10, max_overflow=20`
- **Pagination**: Default 10 items per page
- **Indexes**: Created on frequently queried fields (user_id, student_id, etc.)
- **Query Optimization**: Using SQLAlchemy ORM with eager loading

## 🧪 Testing

```bash
pytest
pytest -v  # Verbose output
pytest --cov  # Coverage report
```

## 📝 API Response Format

### Success Response
```json
{
  "id": "uuid",
  "name": "John Doe",
  "created_at": "2024-01-01T12:00:00"
}
```

### Error Response
```json
{
  "detail": "User not found"
}
```

HTTP Status Codes:
- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## 🚀 Deployment

### On Render:

1. Connect GitHub repository
2. Create new Web Service
3. Set Environment Variables from `.env`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Database Migration (Alembic)

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

## 📞 Support

For issues and questions, refer to the main GETIVA documentation.

---

**GETIVA v1.0.0** | Modern Job Application Tracking System
