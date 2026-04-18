# GETIVA - Quick Start Guide

Modern SaaS platform for job application tracking and consultancy management.

## 📁 Project Structure

```
getiva/
├── index.html                 # Modern landing page
├── styles.css                 # Dark theme with neon accents
├── script.js                  # Frontend interactions
│
├── main.py                    # FastAPI application entry point
├── config.py                  # Environment configuration
├── database.py                # PostgreSQL connection
├── models.py                  # SQLAlchemy ORM models
├── schemas.py                 # Pydantic validation schemas
├── auth.py                    # JWT authentication
├── storage.py                 # Supabase file storage
│
├── routes/                    # API endpoints
│   ├── auth.py               # Authentication (register, login)
│   ├── applications.py        # Job application management
│   ├── payments.py            # Payment tracking
│   ├── analytics.py           # Reports and analytics
│   └── files.py               # File upload/storage
│
├── requirements.txt           # Python dependencies
├── .env                       # Production environment variables
├── .env.example               # Environment template
├── BACKEND_README.md          # Backend documentation
└── QUICKSTART.md             # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL (Neon database configured)
- Node.js (optional, for frontend dev tools)

### 1. Install Dependencies

```bash
cd getiva
pip install -r requirements.txt
```

### 2. Verify Environment Variables

Check `.env` file has:
- `DATABASE_URL`: Neon PostgreSQL connection string ✓
- `SUPABASE_URL`: Supabase project URL ✓
- `SUPABASE_API_KEY`: Supabase API key ✓

All credentials are already configured!

### 3. Initialize Database

The database tables are created automatically on first run, but you can manually create them:

```bash
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 4. Start Backend Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend URL**: http://localhost:8000

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🎨 Frontend

Open `index.html` in your browser to view the modern landing page.

**Features:**
- Ultra-modern dark theme
- Neon blue/orange accents
- Glassmorphism effects
- Smooth animations
- Fully responsive
- Interactive components

## 🔐 Authentication Flow

### 1. Register New User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "role": "student",
    "full_name": "John Doe"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Use Token in Requests

```bash
curl -X GET "http://localhost:8000/api/applications" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 Key API Endpoints

### Applications
- `POST /api/applications` - Create application
- `GET /api/applications` - List applications
- `GET /api/applications/{id}` - Get details
- `PATCH /api/applications/{id}` - Update status
- `DELETE /api/applications/{id}` - Delete

### Payments
- `POST /api/payments/student` - Create student payment
- `POST /api/payments/recruiter` - Create recruiter payment
- `GET /api/payments/student` - List student payments
- `GET /api/payments/recruiter` - List recruiter payments

### Analytics
- `GET /api/analytics/system` - System overview
- `GET /api/analytics/applications` - App statistics
- `GET /api/analytics/recruiters` - Recruiter performance
- `GET /api/analytics/financial` - Financial report
- `GET /api/analytics/daily?days=30` - Daily report

### File Upload
- `POST /api/files/resume` - Upload resume
- `GET /api/files/resume` - Get resume URL
- `GET /api/files/list` - List student files
- `DELETE /api/files/{file_path}` - Delete file

## 👥 Test Accounts

Create test accounts by registering through the API:

```bash
# Admin account
Username: admin_user
Password: AdminPass123!
Role: admin

# Recruiter account
Username: recruiter_user
Password: RecruiterPass123!
Role: recruiter

# Student account
Username: student_user
Password: StudentPass123!
Role: student
```

## 📋 Development Tips

### Database Queries
Access PostgreSQL directly (for debugging):

```python
from database import SessionLocal
from models import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f"{user.username} - {user.role}")
```

### Test File Upload
```bash
curl -X POST "http://localhost:8000/api/files/resume" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"
```

### View Database Logs
Enable SQL logging in development:

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 🔧 Configuration Tips

### Change Token Expiration
Edit `.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Enable Debug Mode
```env
DEBUG=True
ENVIRONMENT=development
```

### Add More CORS Origins
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourfrontend.com
```

## 📊 Database Schema Overview

```
Users
  ├── User ID (UUID)
  ├── username, email
  ├── password_hash
  ├── role (admin, recruiter, student)
  └── created_at, updated_at

Students
  ├── Student ID (UUID)
  ├── user_id (FK)
  ├── full_name
  ├── resume_url (Supabase)
  └── applications, payments (relations)

Recruiters
  ├── Recruiter ID (UUID)
  ├── user_id (FK)
  ├── name
  └── applications, payments (relations)

Applications
  ├── Application ID (UUID)
  ├── student_id, recruiter_id (FK)
  ├── company_name, job_title
  ├── status (applied, interview, offer, etc)
  └── applied_date, created_at

Payments
  ├── Student/Recruiter Payment ID (UUID)
  ├── student_id/recruiter_id (FK)
  ├── amount, payment_type
  ├── status (pending, completed, etc)
  └── created_at, updated_at
```

## ⚠️ Important Notes

1. **Keep `.env` secure** - Never commit to version control
2. **Change SECRET_KEY** - Generate a new one for production
3. **Enable HTTPS** - Use in production only
4. **Database backups** - Configure with Neon console
5. **File storage limits** - 5MB max per file, organize by student

## 🐛 Troubleshooting

### Database Connection Failed
```bash
# Test connection
python -c "from database import engine; print(engine.url)"
```

### API Returns 401 Unauthorized
- Token expired? Use `/api/auth/refresh-token`
- Wrong token format? Must be `Bearer YOUR_TOKEN`
- User disabled? Check user.is_active in database

### Supabase Upload Fails
- Check API key in `.env`
- Verify bucket name: `resumes`
- Ensure file size < 5MB
- Check Supabase project is active

### Port Already in Use
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org
- **Supabase Guide**: https://supabase.com/docs
- **PostgreSQL**: https://www.postgresql.org/docs

## 🚀 Deployment

### Deploy to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Set environment variables from `.env`
5. Deploy!

### Deploy to Railway

```bash
railway login
railway link
railway up
```

## 📞 Support

For detailed API documentation, see `BACKEND_README.md`

---

**GETIVA v1.0.0** | Job Application Tracking System
Built with FastAPI, PostgreSQL, and Supabase
