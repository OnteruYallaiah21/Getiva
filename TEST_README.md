# GETIVA Test Suite Documentation

Comprehensive unit testing suite for API endpoints using pytest and FastAPI TestClient.

## 📁 Test Structure

```
tests/
├── __init__.py
├── test_main.py              # Health check and root endpoint tests
├── test_auth.py              # Authentication endpoint tests
├── test_applications.py       # Application CRUD endpoint tests
├── test_payments.py           # Payment endpoint tests
└── test_analytics.py          # Analytics endpoint tests

conftest.py                   # Pytest fixtures and configuration
pytest.ini                    # Pytest configuration file
```

## 🚀 Quick Start

### Install Dependencies
All testing dependencies are in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_auth.py -v
```

### Run Specific Test
```bash
pytest tests/test_auth.py::TestRegister::test_register_student_success -v
```

## 📊 Test Coverage

### Authentication Tests (`test_auth.py`)
- ✅ User Registration (student, recruiter, admin)
- ✅ Duplicate username/email validation
- ✅ Email format validation
- ✅ User Login (success and failures)
- ✅ Invalid credentials handling
- ✅ Inactive user prevention
- ✅ Token Refresh (success and failures)
- ✅ User Logout
- ✅ Password validation

**Total Tests**: ~15

### Applications Tests (`test_applications.py`)
- ✅ Create Application (recruiter only)
- ✅ Authorization checks (students cannot create)
- ✅ List Applications (role-based filtering)
- ✅ Pagination support
- ✅ Update Application Status
- ✅ Delete Application
- ✅ Nonexistent resource handling
- ✅ Permission validation

**Total Tests**: ~13

### Payments Tests (`test_payments.py`)
- ✅ Create Student Payment (admin only)
- ✅ Create Recruiter Payment (admin only)
- ✅ List Student Payments (role-based)
- ✅ List Recruiter Payments (role-based)
- ✅ Update Payment Status
- ✅ Pagination support
- ✅ Authorization checks
- ✅ Payment Statistics

**Total Tests**: ~12

### Analytics Tests (`test_analytics.py`)
- ✅ System Analytics (admin only)
- ✅ Application Analytics
- ✅ Recruiter Performance Analytics
- ✅ Financial Analytics (admin only)
- ✅ Daily Analytics
- ✅ Authorization checks
- ✅ Response structure validation
- ✅ Custom parameters

**Total Tests**: ~13

### Main App Tests (`test_main.py`)
- ✅ Health Check Endpoint
- ✅ Root Endpoint
- ✅ Swagger UI Availability
- ✅ ReDoc Availability
- ✅ OpenAPI Schema
- ✅ Response structure validation

**Total Tests**: ~6

## 🔧 Pytest Configuration

### pytest.ini Settings
```ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
```

### Markers for Test Categorization
```bash
# Run only auth tests
pytest -m auth

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## 🧬 Fixtures (conftest.py)

### Database Fixtures
- `db` - In-memory SQLite database session for each test
- `client` - FastAPI TestClient with database overrides

### Authentication Fixtures
- `get_auth_token` - Function to generate auth tokens
- `auth_headers` - Headers with valid student token
- `admin_auth_headers` - Headers with valid admin token
- `recruiter_auth_headers` - Headers with valid recruiter token

### Data Fixtures
- `test_user_data` - Sample student user data
- `test_recruiter_data` - Sample recruiter data
- `test_admin_data` - Sample admin data
- `create_test_user` - Factory to create test users

## 🧪 Test Examples

### Example 1: Testing Successful Registration
```python
def test_register_student_success(self, client: TestClient, test_user_data: dict):
    """Test successful student registration."""
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user_data["username"]
```

### Example 2: Testing Authorization
```python
def test_create_application_recruiter(
    self,
    client: TestClient,
    recruiter_auth_headers: dict,
):
    """Test recruiter creating an application."""
    response = client.post(
        "/api/applications",
        json=app_data,
        headers=recruiter_auth_headers,
    )
    assert response.status_code == 201
```

### Example 3: Testing Error Cases
```python
def test_login_invalid_username(self, client: TestClient, test_user_data: dict):
    """Test login with invalid username."""
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "password"},
    )
    assert response.status_code == 401
```

## 🔄 Database Testing Strategy

### In-Memory SQLite
- Uses SQLite `:memory:` database for speed
- Creates fresh database for each test
- Automatically cleans up after each test
- No external database dependencies

### Session Management
```python
@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a test database and session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

## 🔐 Security Testing

### Password Validation
- Weak passwords are rejected
- Password hashing is verified
- Inactive users cannot login

### Authorization Checks
- Role-based access control tested
- Students cannot access admin endpoints
- Recruiters cannot modify admin settings
- Users cannot access others' data

### Token Validation
- Invalid tokens are rejected
- Expired tokens trigger refresh
- Missing tokens return 403 Forbidden

## 📈 Running Tests

### Run All Tests with Verbose Output
```bash
pytest -v
```

### Run Tests and Show Print Statements
```bash
pytest -s
```

### Run Tests with Detailed Failure Info
```bash
pytest -vv --tb=long
```

### Run Tests and Stop on First Failure
```bash
pytest -x
```

### Run Tests in Parallel
```bash
pytest -n auto
```

### Run Only Failed Tests
```bash
pytest --lf
```

## 📊 Coverage Reports

### Generate Coverage Report
```bash
pytest --cov=. --cov-report=html
```

This creates an `htmlcov/index.html` file with detailed coverage information.

### View Coverage in Terminal
```bash
pytest --cov=. --cov-report=term-missing
```

### Set Coverage Threshold
```bash
pytest --cov=. --cov-fail-under=80
```

## 🐛 Common Issues

### Issue: "ModuleNotFoundError: No module named 'main'"
**Solution**: Run pytest from the project root directory
```bash
cd /path/to/getiva
pytest
```

### Issue: "ImportError: cannot import name 'User' from 'models'"
**Solution**: Ensure all model imports are correct in conftest.py

### Issue: "Database is locked"
**Solution**: This shouldn't happen with in-memory SQLite, but if it does, ensure tests aren't running in parallel on persistent databases

### Issue: "Tests pass individually but fail when run together"
**Solution**: Check for shared state in fixtures; ensure each test is isolated with function-scoped fixtures

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-fail-under=80
```

## 📚 Best Practices

### 1. Test Isolation
- Each test is independent
- Uses in-memory database
- No test interdependencies
- Database resets between tests

### 2. Descriptive Names
- Test names describe what is being tested
- Use `test_<function>_<scenario>`
- Example: `test_login_invalid_password`

### 3. Arrange-Act-Assert Pattern
```python
def test_example(self):
    # Arrange: Set up test data
    user_data = {"username": "test", "email": "test@example.com"}
    
    # Act: Execute the action
    response = client.post("/api/auth/register", json=user_data)
    
    # Assert: Verify the result
    assert response.status_code == 201
```

### 4. Test Both Success and Failure
- Test happy path (success cases)
- Test edge cases
- Test error conditions
- Test authorization

### 5. Use Fixtures for Setup
- Centralize common setup in conftest.py
- Use fixtures instead of duplicating code
- Factory fixtures for creating test data

## 🎯 Test Metrics

| Category | Count | Coverage |
|----------|-------|----------|
| Auth Tests | 15 | ~95% |
| Application Tests | 13 | ~90% |
| Payment Tests | 12 | ~85% |
| Analytics Tests | 13 | ~80% |
| Main App Tests | 6 | ~100% |
| **Total** | **59** | **~90%** |

## 📖 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

## 🔄 Continuous Testing Workflow

### Development Workflow
1. Write test for new feature
2. Run test (should fail)
3. Implement feature
4. Run test (should pass)
5. Refactor and rerun tests

### Before Committing
```bash
# Run all tests
pytest

# Check coverage
pytest --cov=. --cov-report=term-missing

# Fix any issues
```

### Before Pushing
```bash
# Run full test suite with coverage
pytest -v --cov=. --cov-fail-under=80
```

---

**GETIVA Test Suite** | Pytest v7.4+
Comprehensive API endpoint testing for production-ready code.
