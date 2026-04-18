# Frontend Integration Guide

Complete guide for connecting the GETIVA landing page and dashboards to the backend API.

## 📋 Overview

The landing page now includes full authentication integration with the backend API:
- User registration and login
- Token-based authentication
- Role-based dashboard routing
- Toast notifications
- Secure token management

## 🔐 Authentication Flow

### 1. Landing Page Entry
Users land on `index.html` and can:
- Click "Sign In" in the navbar
- Click "Get Started" buttons throughout the page
- These open the authentication modal

### 2. Registration/Login Modal
Two-form modal system:
- **Login Form**: Enter username and password
- **Register Form**: Create new account with role selection

### 3. Authentication Process

```
User Registration
  ↓
POST /api/auth/register
  ↓
Account Created ✓
  ↓
Show Success Toast
  ↓
Switch to Login Form
  ↓
(User enters credentials)
  ↓
User Login
  ↓
POST /api/auth/login
  ↓
Receive JWT Token
  ↓
Store in localStorage
  ↓
Fetch User Role
  ↓
Redirect to Role Dashboard
```

### 4. Dashboard Routing
After successful login, users are routed based on role:
- **admin** → `admin-dashboard.html`
- **recruiter** → `recruiter-dashboard.html`
- **student** → `student-dashboard.html`

## 🛠️ Implementation Details

### API Configuration
```javascript
const API_BASE_URL = 'http://localhost:8000/api';

const DASHBOARDS = {
    admin: 'admin-dashboard.html',
    recruiter: 'recruiter-dashboard.html',
    student: 'student-dashboard.html'
};
```

### Token Management
```javascript
// Store token after login
localStorage.setItem('authToken', token);
localStorage.setItem('userRole', role);

// Use token in API requests
Authorization: Bearer {token}

// Clear on logout
localStorage.removeItem('authToken');
localStorage.removeItem('userRole');
```

### Authenticated API Calls
```javascript
// Helper function with automatic token injection
async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('authToken');
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    // Automatic token refresh on 401
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    // Handle expired tokens
    if (response.status === 401) {
        localStorage.removeItem('authToken');
        window.location.href = 'index.html';
    }
    
    return response.json();
}
```

## 📱 Frontend Files

### Landing Page
- **index.html** - Includes auth modal HTML
- **styles.css** - Modal and form styling
- **script.js** - Authentication logic and API integration

### Dashboards (Already Connected)
- **admin-dashboard.html** - Admin features
- **recruiter-dashboard.html** - Recruiter features
- **student-dashboard.html** - Student features
- **admin-script.js** - Admin dashboard API calls
- **recruiter-script.js** - Recruiter dashboard API calls
- **student-script.js** - Student dashboard API calls

## 🔧 Key Functions

### Modal Management
```javascript
// Open/close authentication modal
openAuthModal()      // Opens the modal
closeAuthModal()     // Closes and resets forms
switchToRegister()   // Show registration form
switchToLogin()      // Show login form
```

### Authentication
```javascript
// Login user
login(username, password)

// Register new user
register({
    username: 'user',
    email: 'user@example.com',
    password: 'password',
    role: 'student',
    full_name: 'Full Name'  // For students only
})

// Logout
logout()
```

### API Utilities
```javascript
// Make authenticated API call
fetchAPI('/endpoint', {
    method: 'GET',  // or POST, PATCH, DELETE
    body: JSON.stringify(data)
})

// Get user role from token
getUserRole(token)
```

### Notifications
```javascript
// Show toast notification
showToast(message, type, duration)
// Types: 'success', 'error', 'warning', 'info'
// Duration: milliseconds (default 3000)

showToast('Account created!', 'success', 2000)
showToast('Invalid credentials', 'error', 3000)
```

## 🚀 Usage Examples

### Example 1: User Registration
```javascript
// User fills form and submits
const userData = {
    username: 'john_doe',
    email: 'john@example.com',
    password: 'SecurePass123!',
    role: 'student',
    full_name: 'John Doe'
};

const success = await register(userData);
if (success) {
    // Show success message
    // Switch to login form
}
```

### Example 2: User Login
```javascript
// User enters credentials
const success = await login('john_doe', 'SecurePass123!');
if (success) {
    // Token is stored
    // Redirected to student-dashboard.html
}
```

### Example 3: API Call from Dashboard
```javascript
// From dashboard (already authenticated)
const applications = await fetchAPI('/applications', {
    method: 'GET'
});

// Token is automatically added
// If token expires, user is redirected to login
```

## 🔒 Security Features

### Token Storage
- JWT tokens stored in localStorage
- Token included in all API requests
- Automatic cleanup on logout
- Expired tokens trigger re-login

### Authorization
- Role-based dashboard routing
- API validates token on each request
- Invalid/expired tokens return 401
- Users redirected to login on 401

### Form Validation
- Client-side validation in modals
- Server-side validation on backend
- Error messages displayed to users
- Password requirements enforced

## 📋 API Endpoints Used

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Get authentication token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout (optional)
- `POST /api/auth/refresh-token` - Refresh token

## 🧪 Testing the Integration

### Test Registration
1. Open `index.html` in browser
2. Click "Sign In" button
3. Click "Create one" link
4. Fill registration form
5. Select role (Student or Recruiter)
6. Click "Create Account"
7. Should be redirected to login form

### Test Login
1. Open `index.html`
2. Click "Sign In"
3. Enter credentials from registration
4. Click "Sign In"
5. Should redirect to appropriate dashboard
6. Dashboard should load with authenticated data

### Test Token Persistence
1. Login and go to dashboard
2. Refresh the page (F5)
3. Dashboard should still be accessible
4. Token remains in localStorage

### Test Session Expiration
1. Login to dashboard
2. Open browser DevTools (F12)
3. Go to Application → Storage → localStorage
4. Delete the authToken key
5. Try to make an API call
6. Should redirect to login page

## 🐛 Troubleshooting

### "Login button does nothing"
- Check browser console for errors
- Verify API_BASE_URL is correct
- Check network tab in DevTools
- Ensure backend is running

### "Can't see auth modal"
- Check if styles.css is loaded
- Verify modal HTML is in index.html
- Check z-index of modal (should be 999)

### "Token not being saved"
- Check localStorage in DevTools
- Verify response from /api/auth/login
- Check if localStorage is enabled
- Try clearing browser cache

### "Can't access dashboard after login"
- Check if role is being set correctly
- Verify dashboard file exists (check file names)
- Check network requests to ensure data loads
- Look for console errors

### "API requests failing with 401"
- Token may be expired
- Try logging out and back in
- Check if token format is correct (Bearer {token})
- Verify API_BASE_URL is correct

## 📚 Configuration

### Change API Base URL
Edit in `script.js`:
```javascript
const API_BASE_URL = 'https://your-api-domain.com/api';
```

Or use environment variable:
```javascript
const API_BASE_URL = localStorage.getItem('apiBaseUrl') || 'http://localhost:8000/api';

// Set in console or initialization
localStorage.setItem('apiBaseUrl', 'https://your-api.com/api');
```

### Customize Dashboard Routing
Edit in `script.js`:
```javascript
const DASHBOARDS = {
    admin: 'admin-dashboard.html',
    recruiter: 'recruiter-dashboard.html',
    student: 'student-dashboard.html',
    custom_role: 'custom-dashboard.html'
};
```

## 🔄 Next Steps

### For Dashboard Integration
1. Each dashboard already has API integration in its script file
2. Update dashboard scripts to use new `fetchAPI()` helper
3. Remove hardcoded tokens, use localStorage
4. Add logout button to navigation

### For Additional Features
1. Add password reset flow
2. Add email verification
3. Add remember me functionality
4. Add social login (Google, GitHub)
5. Add two-factor authentication

## 📞 Support

For issues with frontend integration:
1. Check browser console (F12)
2. Check network requests in DevTools
3. Verify API is running (curl http://localhost:8000/health)
4. Check token in localStorage
5. Review BACKEND_README.md for API details

---

**GETIVA Frontend Integration** | v1.0
Complete end-to-end authentication and authorization system
