# GETIVA - Job Application Tracking Platform

A comprehensive job application tracking and consultancy management system built with FastAPI (backend) and modern web technologies (frontend).

## Project Structure

```
Getiva/
├── backend/              # FastAPI REST API
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database setup
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic validation schemas
│   ├── auth.py          # JWT authentication
│   ├── storage.py       # File storage operations
│   ├── routes/          # API endpoint routes
│   ├── alembic/         # Database migrations
│   ├── tests/           # Unit tests
│   └── requirements.txt  # Python dependencies
├── frontend/            # Web interface
│   ├── public/          # HTML files
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files
└── docs/                # Documentation
```

## Features

- **User Management**: Registration, authentication, role-based access control (Admin, Recruiter, Student)
- **Application Tracking**: Create, update, and monitor job applications
- **Payment Management**: Handle student and recruiter payments
- **Analytics**: Dashboard with insights and reporting
- **File Storage**: Resume and document uploads via Supabase
- **Database Migrations**: Alembic for schema versioning
- **Comprehensive Tests**: Unit tests for all API endpoints

## Prerequisites

- Python 3.8+
- PostgreSQL or SQLite database
- pip (Python package manager)
- Supabase account (optional, for file storage)

## Setup Instructions

### 1. Create Virtual Environment

#### On Linux/macOS:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 2. Install Requirements

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Environment Setup

Copy the example environment file and configure it:

```bash
# From backend directory
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=sqlite:///./test.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/getiva

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# App Settings
APP_NAME=GETIVA
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True
PORT=8000

# CORS Origins
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000

# Supabase (optional, for file storage)
SUPABASE_URL=your-supabase-url
SUPABASE_API_KEY=your-supabase-key
SUPABASE_BUCKET=your-bucket-name
```

### 4. Initialize Database

```bash
# From backend directory
# Run migrations
alembic upgrade head

# Or create tables directly
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

## Running the Application

### Backend API

```bash
# From backend directory (with venv activated)
python main.py
```

The API will be available at: `http://localhost:8000`

API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend

```bash
# From project root, serve frontend files
python -m http.server 8000 --directory frontend/public
```

Then open your browser to: `http://localhost:8000`

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `POST /refresh` - Refresh JWT token
- `POST /logout` - User logout

### Applications (`/api/applications`)
- `POST /` - Create application
- `GET /` - List applications
- `GET /{id}` - Get application details
- `PUT /{id}` - Update application
- `DELETE /{id}` - Delete application

### Payments (`/api/payments`)
- `POST /student` - Create student payment
- `POST /recruiter` - Create recruiter payment
- `GET /` - List payments
- `GET /{id}` - Get payment details

### Analytics (`/api/analytics`)
- `GET /applications` - Application statistics
- `GET /recruiter` - Recruiter performance
- `GET /daily-report` - Daily report
- `GET /financial` - Financial report
- `GET /system` - System analytics

### Files (`/api/files`)
- `POST /resume` - Upload resume
- `POST /document` - Upload document
- `GET /{file_id}` - Download file
- `DELETE /{file_id}` - Delete file

## Running Tests

```bash
# From backend directory (with venv activated)
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Database Migrations

```bash
# From backend directory

# Create new migration
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Development Notes

### Deactivate Virtual Environment

```bash
# When done, deactivate venv
deactivate
```

### Important Files

- `backend/config.py` - Application configuration
- `backend/models.py` - Database models (7 tables)
- `backend/schemas.py` - Data validation schemas
- `backend/auth.py` - Authentication utilities (JWT, bcrypt)
- `backend/storage.py` - File storage integration

### Frontend Files

- `frontend/public/index.html` - Landing page
- `frontend/public/admin-dashboard.html` - Admin interface
- `frontend/public/student-dashboard.html` - Student interface
- `frontend/public/recruiter-dashboard.html` - Recruiter interface
- `frontend/css/design-system.css` - Design system and components
- `frontend/js/script.js` - Main frontend logic

## Troubleshooting

### Module Not Found Error

Ensure you're in the correct directory and venv is activated:
```bash
# Check you're in project root
ls backend/main.py  # should exist

# Check venv is active
which python  # should show path to venv
```

### Database Connection Error

Check your `DATABASE_URL` in `.env`:
```bash
# For SQLite (default)
DATABASE_URL=sqlite:///./test.db

# For PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/getiva
```

### Port Already in Use

Change the port in `backend/config.py` or `.env`:
```bash
# Run on different port
PORT=8001 python main.py
```

### Cryptography/SSL Issues

Reinstall cryptography dependencies:
```bash
pip install --upgrade cryptography
pip install email-validator
```

## Documentation

See the `docs/` directory for detailed documentation:
- `BACKEND_README.md` - Backend architecture details
- `FRONTEND_INTEGRATION.md` - Frontend-backend integration
- `TESTING_REPORT.md` - Test results and coverage
- `MIGRATIONS.md` - Database migration guide
- `QUICKSTART.md` - Quick start guide

## Support

For issues or questions, check:
1. The documentation in `docs/` directory
2. API documentation at `/docs` endpoint
3. Test files in `backend/tests/` for usage examples

## License

Proprietary - GETIVA Platform
