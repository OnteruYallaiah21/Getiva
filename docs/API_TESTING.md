# GETIVA API Testing Guide

Complete guide to test all GETIVA API endpoints.

## 🛠️ Setup

### 1. Install cURL or Use Postman
```bash
# macOS
brew install curl

# Ubuntu
sudo apt-get install curl

# Or use Postman: https://www.postman.com/downloads/
```

### 2. Start Backend
```bash
python main.py
# Server runs on http://localhost:8000
```

## 🔑 Authentication Tests

### Register New Student

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student_test",
    "email": "student@test.com",
    "password": "TestPass123!",
    "role": "student",
    "full_name": "Test Student"
  }'
```

### Register Recruiter

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "recruiter_test",
    "email": "recruiter@test.com",
    "password": "RecruiterPass123!",
    "role": "recruiter",
    "full_name": "Test Recruiter"
  }'
```

### Login User

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student_test",
    "password": "TestPass123!"
  }'
```

**Save the `access_token` from response for further requests**

```bash
# Store token in variable (bash)
TOKEN="your_access_token_here"
```

## 📝 Application Tests

### Create Application

```bash
curl -X POST "http://localhost:8000/api/applications" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "student_id": "student_uuid_here",
    "company_name": "Google",
    "job_title": "Senior Engineer",
    "job_description": "Looking for experienced engineers",
    "job_url": "https://google.com/careers/senior-engineer",
    "notes": "Strong candidate, excellent portfolio"
  }'
```

### List Applications

```bash
# All applications
curl -X GET "http://localhost:8000/api/applications" \
  -H "Authorization: Bearer $TOKEN"

# Filter by student
curl -X GET "http://localhost:8000/api/applications?student_id=uuid" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/applications?status=applied" \
  -H "Authorization: Bearer $TOKEN"

# Pagination
curl -X GET "http://localhost:8000/api/applications?page=1&per_page=20" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Application Details

```bash
curl -X GET "http://localhost:8000/api/applications/application_id_here" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Application Status

```bash
curl -X PATCH "http://localhost:8000/api/applications/application_id_here" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "interview",
    "notes": "Interview scheduled for next week"
  }'
```

### Delete Application

```bash
curl -X DELETE "http://localhost:8000/api/applications/application_id_here" \
  -H "Authorization: Bearer $TOKEN"
```

## 💰 Payment Tests

### Create Student Payment

```bash
curl -X POST "http://localhost:8000/api/payments/student" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "student_id": "student_uuid_here",
    "amount": 500.00,
    "payment_type": "service_fee",
    "notes": "Monthly subscription fee"
  }'
```

### Create Recruiter Payment

```bash
curl -X POST "http://localhost:8000/api/payments/recruiter" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "recruiter_id": "recruiter_uuid_here",
    "amount": 2000.00,
    "salary_month": "2024-01",
    "notes": "January salary"
  }'
```

### List Student Payments

```bash
curl -X GET "http://localhost:8000/api/payments/student" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/payments/student?status=completed" \
  -H "Authorization: Bearer $TOKEN"
```

### List Recruiter Payments

```bash
curl -X GET "http://localhost:8000/api/payments/recruiter" \
  -H "Authorization: Bearer $TOKEN"

# Filter by month
curl -X GET "http://localhost:8000/api/payments/recruiter?salary_month=2024-01" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Payment Status

```bash
curl -X PATCH "http://localhost:8000/api/payments/student/payment_id_here" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "status": "completed",
    "notes": "Payment processed"
  }'
```

## 📊 Analytics Tests

### Get Application Statistics

```bash
curl -X GET "http://localhost:8000/api/analytics/applications" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Recruiter Performance

```bash
curl -X GET "http://localhost:8000/api/analytics/recruiters" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Daily Report

```bash
# Last 30 days
curl -X GET "http://localhost:8000/api/analytics/daily" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Last 7 days
curl -X GET "http://localhost:8000/api/analytics/daily?days=7" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Last 90 days
curl -X GET "http://localhost:8000/api/analytics/daily?days=90" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Financial Report

```bash
curl -X GET "http://localhost:8000/api/analytics/financial" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Complete System Analytics

```bash
curl -X GET "http://localhost:8000/api/analytics/system" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Recruiter Specific Stats

```bash
curl -X GET "http://localhost:8000/api/analytics/recruiter/recruiter_uuid_here/stats" \
  -H "Authorization: Bearer $TOKEN"
```

## 📤 File Upload Tests

### Upload Resume

```bash
curl -X POST "http://localhost:8000/api/files/resume" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/resume.pdf"
```

### Get Resume URL

```bash
curl -X GET "http://localhost:8000/api/files/resume" \
  -H "Authorization: Bearer $TOKEN"
```

### List Student Files

```bash
curl -X GET "http://localhost:8000/api/files/list" \
  -H "Authorization: Bearer $TOKEN"
```

### Delete File

```bash
curl -X DELETE "http://localhost:8000/api/files/file_path_here" \
  -H "Authorization: Bearer $TOKEN"
```

## ✅ Test Scenarios

### Scenario 1: Complete Job Application Workflow

1. **Register student**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "jane_doe",
       "email": "jane@example.com",
       "password": "JanePass123!",
       "role": "student"
     }'
   ```

2. **Login and save token**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "jane_doe",
       "password": "JanePass123!"
     }'
   ```

3. **Upload resume**
   ```bash
   curl -X POST "http://localhost:8000/api/files/resume" \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@resume.pdf"
   ```

4. **Register recruiter**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_recruiter",
       "email": "john@recruiter.com",
       "password": "JohnPass123!",
       "role": "recruiter"
     }'
   ```

5. **Recruiter creates application**
   - Use student_id from step 1
   - Use recruiter's token from step 4

6. **View application statistics**
   ```bash
   curl -X GET "http://localhost:8000/api/analytics/applications" \
     -H "Authorization: Bearer $TOKEN"
   ```

### Scenario 2: Payment Processing

1. **Create student payment**
2. **Create recruiter payment**
3. **View financial report**
4. **Update payment status**

## 📋 Expected Response Examples

### Successful Registration
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "student_test",
  "email": "student@test.com",
  "role": "student",
  "is_active": 1,
  "created_at": "2024-01-15T10:30:00"
}
```

### Successful Login
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Application List
```json
{
  "total": 25,
  "page": 1,
  "per_page": 10,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "student_id": "550e8400-e29b-41d4-a716-446655440001",
      "recruiter_id": "550e8400-e29b-41d4-a716-446655440002",
      "company_name": "Google",
      "job_title": "Senior Engineer",
      "status": "interview",
      "applied_date": "2024-01-10T08:00:00",
      "created_at": "2024-01-10T08:00:00"
    }
  ]
}
```

### System Analytics
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

## ⚠️ Common Errors

### 401 Unauthorized
- Token is missing or expired
- Solution: Login again and use new token

### 403 Forbidden
- User role doesn't have permission
- Solution: Use appropriate user role

### 404 Not Found
- Resource doesn't exist
- Solution: Check resource ID is correct

### 422 Validation Error
- Invalid request data
- Solution: Check field types and required fields

## 🔗 Using Postman

1. Create new Collection
2. Add each endpoint as a request
3. Use environment variables for `$TOKEN`
4. Set Authorization header: `Bearer {{TOKEN}}`
5. Export collection for team

## 📊 Performance Testing

```bash
# Test concurrent requests
for i in {1..10}; do
  curl -X GET "http://localhost:8000/api/applications" \
    -H "Authorization: Bearer $TOKEN" &
done
wait
```

---

**Happy Testing!** 🚀
