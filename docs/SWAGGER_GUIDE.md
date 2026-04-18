# Swagger API Guide

## Quick Access

Once the backend is running (`python main.py`), access the API documentation at:

### Interactive Swagger UI
**http://localhost:8000/docs**

Features:
- Try out endpoints directly in your browser
- See live request/response examples
- Auto-completion for parameters
- Real-time API exploration
- Download OpenAPI schema

### Alternative Documentation (ReDoc)
**http://localhost:8000/redoc**

Features:
- Clean, readable documentation layout
- Better for reading API specifications
- Search functionality
- API examples and descriptions

### Raw OpenAPI Specification
**http://localhost:8000/openapi.json**

- Machine-readable OpenAPI 3.0.0 specification
- Use with third-party tools
- Import into Postman, Insomnia, etc.

---

## Using Swagger UI (Recommended)

### 1. Start the Backend
```bash
cd backend
python main.py
```

Output should show:
```
🚀 Starting GETIVA v1.0.0
📊 Environment: development
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Open Swagger UI
Go to: **http://localhost:8000/docs**

You should see a page titled "GETIVA API" with all endpoints listed.

### 3. Test Authentication Flow

#### Step 1: Register a User
1. Click on **POST /api/auth/register**
2. Click "Try it out"
3. Enter this in the request body:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!",
  "role": "student"
}
```
4. Click "Execute"
5. You should see status 201 with user details

#### Step 2: Login
1. Click on **POST /api/auth/login**
2. Click "Try it out"
3. Enter:
```json
{
  "username": "testuser",
  "password": "SecurePass123!"
}
```
4. Click "Execute"
5. Copy the `access_token` value

#### Step 3: Authorize Subsequent Requests
1. Click the green "Authorize" button at top right
2. In "Bearer" field, paste the token (just the token, no "Bearer " prefix needed)
3. Click "Authorize"
4. Close the dialog
5. All subsequent requests will include your token

### 4. Test Creating an Application
1. Ensure you're authorized (see step 3 above)
2. Click on **POST /api/applications**
3. Click "Try it out"
4. Enter:
```json
{
  "job_title": "Senior Developer",
  "company_name": "Tech Company",
  "job_url": "https://example.com/jobs/123",
  "salary_min": 80000,
  "salary_max": 120000,
  "status": "applied",
  "notes": "Great opportunity"
}
```
5. Click "Execute"

---

## Common Swagger UI Operations

### View Endpoint Details
- Click on any endpoint to expand it
- Shows description, parameters, request/response schema
- Lists required vs optional fields

### Try Different HTTP Methods
- **GET**: Retrieve data
- **POST**: Create new data
- **PUT**: Update existing data
- **DELETE**: Remove data

### Filter Endpoints by Tag
- Use the tag buttons at left to show/hide endpoint groups:
  - Auth
  - Applications
  - Payments
  - Analytics
  - Files

### Download OpenAPI Schema
1. Click the blue "Download" button at top
2. Saves as `swagger.json` or `openapi.json`
3. Use with Postman, Insomnia, or code generators

---

## Exporting OpenAPI Schema

### Option 1: Via Swagger UI
As described above, click the Download button.

### Option 2: Using the Export Script
```bash
cd backend
python export_openapi.py
```

Output:
```
✓ OpenAPI schema exported to openapi.json
✓ Schema contains 25 endpoints
✓ OpenAPI version: 3.0.2
```

### Option 3: Direct Download
```bash
# With curl
curl http://localhost:8000/openapi.json > openapi.json

# With wget
wget http://localhost:8000/openapi.json
```

---

## Using with Other Tools

### Postman
1. Open Postman
2. File > Import
3. Enter URL: `http://localhost:8000/openapi.json`
4. Click Import
5. Full API collection imported with all endpoints

### Insomnia
1. Open Insomnia
2. Create New > Import from URL
3. Enter: `http://localhost:8000/openapi.json`
4. Endpoints automatically created

### VS Code REST Client
```rest
### Get API Info
GET http://localhost:8000/ HTTP/1.1

### Register User
POST http://localhost:8000/api/auth/register HTTP/1.1
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!",
  "role": "student"
}
```

---

## API Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET request successful |
| 201 | Created | POST/PUT request successful |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Internal server error |

---

## Example API Workflows

### Workflow 1: Job Application Tracking (Student)
1. Register → /api/auth/register
2. Login → /api/auth/login
3. Create Application → POST /api/applications
4. Update Status → PUT /api/applications/{id}
5. View Applications → GET /api/applications
6. Upload Resume → POST /api/files/resume

### Workflow 2: Recruiter Management (Recruiter)
1. Register as Recruiter → /api/auth/register
2. Login → /api/auth/login
3. Create Job Posts → POST /api/applications
4. View Analytics → GET /api/analytics/recruiter
5. Manage Payments → POST /api/payments/recruiter

### Workflow 3: System Administration (Admin)
1. Login as Admin → /api/auth/login
2. View System Analytics → GET /api/analytics/system
3. View All Payments → GET /api/payments
4. View Daily Reports → GET /api/analytics/daily-report

---

## Troubleshooting

### 401 Unauthorized
- Token has expired → Login again
- Token format wrong → Don't include "Bearer " prefix in Authorize field
- Missing Authorization header → Use Authorize button in UI

### 403 Forbidden
- Your role doesn't have permission
- Example: Students can't view admin analytics
- Check endpoint documentation for required role

### 422 Validation Error
- Check request body schema in Swagger UI
- Ensure all required fields are present
- Verify data types match schema

### Connection Refused
- Backend not running → Run `python main.py`
- Wrong port → Default is 8000
- Check if firewall is blocking connections

---

## API Documentation Files

See related documentation:
- **API_DOCUMENTATION.md** - Complete endpoint reference
- **README.md** - Project setup and general info
- **BACKEND_README.md** - Backend architecture
- **TEST_README.md** - Running tests

---

## Next Steps

1. Test all endpoints in Swagger UI
2. Export OpenAPI schema for your client
3. Generate API client libraries if needed
4. Review API_DOCUMENTATION.md for details
5. Check TESTING_REPORT.md for endpoint test coverage
