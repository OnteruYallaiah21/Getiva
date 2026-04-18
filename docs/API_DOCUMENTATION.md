# GETIVA API Documentation

Complete REST API documentation for GETIVA - Job Application Tracking Platform.

## Quick Start

### Access Swagger UI
Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Authentication
All protected endpoints require a JWT token. Include it in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
http://localhost:8000/api
```

## User Roles
- **ADMIN**: Full system access, user management, analytics
- **RECRUITER**: Create and manage applications, view analytics
- **STUDENT**: Track applications, upload documents

---

## Authentication Endpoints (`/api/auth`)

### 1. Register User
**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "role": "student",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "student",
  "full_name": "John Doe"
}
```

### 2. Login
**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 3. Refresh Token
**POST** `/api/auth/refresh`

Get a new access token using the current token.

**Headers:**
```
Authorization: Bearer <current_token>
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 4. Logout
**POST** `/api/auth/logout`

Logout user (invalidate token).

**Headers:**
```
Authorization: Bearer <your_token>
```

---

## Applications Endpoints (`/api/applications`)

### 1. Create Application
**POST** `/api/applications`

Create a new job application. **Requires: RECRUITER or ADMIN role**

**Request Body:**
```json
{
  "job_title": "Senior Python Developer",
  "company_name": "Tech Corp",
  "job_url": "https://example.com/jobs/123",
  "salary_min": 80000,
  "salary_max": 120000,
  "status": "applied",
  "applied_date": "2024-04-18T10:00:00Z",
  "notes": "Great opportunity for growth"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "job_title": "Senior Python Developer",
  "company_name": "Tech Corp",
  "status": "applied",
  "created_at": "2024-04-18T10:00:00Z"
}
```

### 2. List Applications
**GET** `/api/applications`

Get all applications (with filters).

**Query Parameters:**
- `status` (optional): Filter by status (applied, interview, offer, rejected)
- `company` (optional): Filter by company name
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 10)

**Response (200):**
```json
{
  "total": 25,
  "skip": 0,
  "limit": 10,
  "applications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "job_title": "Senior Python Developer",
      "company_name": "Tech Corp",
      "status": "applied",
      "created_at": "2024-04-18T10:00:00Z"
    }
  ]
}
```

### 3. Get Application Details
**GET** `/api/applications/{application_id}`

Get detailed information about a specific application.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "job_title": "Senior Python Developer",
  "company_name": "Tech Corp",
  "job_url": "https://example.com/jobs/123",
  "salary_min": 80000,
  "salary_max": 120000,
  "status": "applied",
  "applied_date": "2024-04-18T10:00:00Z",
  "notes": "Great opportunity",
  "created_at": "2024-04-18T10:00:00Z",
  "updated_at": "2024-04-18T10:00:00Z"
}
```

### 4. Update Application
**PUT** `/api/applications/{application_id}`

Update an existing application.

**Request Body:**
```json
{
  "status": "interview",
  "notes": "Interview scheduled for Friday"
}
```

**Response (200):** Updated application object

### 5. Delete Application
**DELETE** `/api/applications/{application_id}`

Delete an application.

**Response (200):**
```json
{
  "message": "Application deleted successfully"
}
```

---

## Payments Endpoints (`/api/payments`)

### 1. Create Student Payment
**POST** `/api/payments/student`

Record a student payment. **Requires: STUDENT or ADMIN role**

**Request Body:**
```json
{
  "amount": 99.99,
  "payment_method": "credit_card",
  "description": "Premium subscription - 3 months",
  "due_date": "2024-05-18"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": "student-uuid",
  "amount": 99.99,
  "status": "pending",
  "created_at": "2024-04-18T10:00:00Z"
}
```

### 2. Create Recruiter Payment
**POST** `/api/payments/recruiter`

Record a recruiter payment. **Requires: RECRUITER or ADMIN role**

**Request Body:**
```json
{
  "amount": 299.99,
  "payment_method": "bank_transfer",
  "description": "Monthly subscription",
  "due_date": "2024-05-18"
}
```

**Response (201):** Recruiter payment object

### 3. List Payments
**GET** `/api/payments`

Get all payments with filters. **Requires: ADMIN role**

**Query Parameters:**
- `status` (optional): Filter by status (pending, completed, failed)
- `user_type` (optional): student or recruiter
- `skip` (optional): Pagination offset
- `limit` (optional): Results per page

**Response (200):**
```json
{
  "total": 15,
  "payments": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "amount": 99.99,
      "status": "pending",
      "created_at": "2024-04-18T10:00:00Z"
    }
  ]
}
```

### 4. Get Payment Details
**GET** `/api/payments/{payment_id}`

Get details of a specific payment.

**Response (200):** Payment object with all details

---

## Analytics Endpoints (`/api/analytics`)

### 1. Application Statistics
**GET** `/api/analytics/applications`

Get application statistics. **Requires: RECRUITER or ADMIN role**

**Response (200):**
```json
{
  "total_applications": 25,
  "by_status": {
    "applied": 10,
    "interview": 8,
    "offer": 5,
    "rejected": 2
  },
  "by_company": {
    "Tech Corp": 5,
    "StartUp Inc": 3,
    "Other": 17
  }
}
```

### 2. Recruiter Performance
**GET** `/api/analytics/recruiter`

Get recruiter performance metrics. **Requires: ADMIN role**

**Query Parameters:**
- `recruiter_id` (optional): Filter by recruiter

**Response (200):**
```json
{
  "total_posts": 45,
  "total_applications": 120,
  "average_rating": 4.5,
  "successful_hires": 12,
  "active_jobs": 8
}
```

### 3. Daily Report
**GET** `/api/analytics/daily-report`

Get daily activity report. **Requires: ADMIN role**

**Response (200):**
```json
{
  "date": "2024-04-18",
  "new_users": 5,
  "new_applications": 12,
  "completed_payments": 3,
  "total_revenue": 299.97
}
```

### 4. Financial Report
**GET** `/api/analytics/financial`

Get financial report. **Requires: ADMIN role**

**Query Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Response (200):**
```json
{
  "period": {
    "start": "2024-04-01",
    "end": "2024-04-30"
  },
  "total_revenue": 15000.00,
  "student_payments": 9000.00,
  "recruiter_payments": 6000.00,
  "payment_count": 150
}
```

### 5. System Analytics
**GET** `/api/analytics/system`

Get overall system analytics. **Requires: ADMIN role**

**Response (200):**
```json
{
  "total_users": 500,
  "user_breakdown": {
    "students": 350,
    "recruiters": 140,
    "admins": 10
  },
  "total_applications": 2500,
  "total_revenue": 75000.00,
  "system_uptime": "99.9%"
}
```

---

## Files Endpoints (`/api/files`)

### 1. Upload Resume
**POST** `/api/files/resume`

Upload a resume file. **Requires: STUDENT role**

**Form Data:**
- `file` (required): PDF, DOC, DOCX, or TXT file (max 5MB)

**Response (200):**
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "resume.pdf",
  "size": 245000,
  "url": "https://storage.example.com/resumes/resume.pdf",
  "uploaded_at": "2024-04-18T10:00:00Z"
}
```

### 2. Upload Document
**POST** `/api/files/document`

Upload a supporting document. **Requires: STUDENT or RECRUITER role**

**Form Data:**
- `file` (required): PDF, DOC, DOCX, or TXT file (max 5MB)
- `document_type` (optional): cover_letter, portfolio, certificate, etc.

**Response (200):** File object with URL

### 3. Download File
**GET** `/api/files/{file_id}`

Download a file by ID.

**Response (200):** File content (binary)

### 4. Delete File
**DELETE** `/api/files/{file_id}`

Delete a file.

**Response (200):**
```json
{
  "message": "File deleted successfully"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes
- `200`: OK - Request successful
- `201`: Created - Resource created successfully
- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Missing or invalid token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server error

---

## Testing with cURL

### Example: Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "role": "student"
  }'
```

### Example: Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123!"
  }'
```

### Example: Create Application (with auth)
```bash
curl -X POST "http://localhost:8000/api/applications" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Developer",
    "company_name": "Tech Corp",
    "status": "applied"
  }'
```

---

## Rate Limiting

Currently no rate limiting is enforced. Future versions may implement:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

---

## Support

For issues or questions:
1. Check Swagger UI at `/docs`
2. Review test files in `backend/tests/`
3. Check the README for setup instructions
