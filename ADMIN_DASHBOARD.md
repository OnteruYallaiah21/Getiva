# GETIVA Admin Dashboard

Complete administrative interface for managing the GETIVA platform.

## 🎯 Overview

The Admin Dashboard provides comprehensive tools for administrators to manage users, applications, payments, and view system analytics.

**URL**: `admin-dashboard.html`

---

## 📊 Dashboard Sections

### 1. Dashboard (Home)

**Overview of system statistics:**
- Total Students
- Total Recruiters  
- Total Applications
- Total Revenue

**Visual Elements:**
- Quick stat cards with icons
- Application status distribution chart
- Financial overview (Revenue, Paid, Profit)
- Recent applications table

**Key Metrics:**
```
Students: 150
Recruiters: 25
Applications: 4,500
Revenue: $45,230
```

---

### 2. User Management

**Manage all system users:**

**Features:**
- View all users (students, recruiters, admins)
- Create new users via modal form
- Edit user details
- Toggle user active/inactive status
- Filter by role and status
- Pagination support

**User Data:**
- Username
- Email
- Role (student, recruiter, admin)
- Status (active/inactive)
- Join date
- Action buttons

**Filters:**
- By role (All, Students, Recruiters, Admins)
- By status (All, Active, Inactive)

**User Creation Form:**
```
- Username (required)
- Email (required)
- Password (required)
- Role (dropdown)
- Full Name (optional)
```

---

### 3. Applications

**Manage job applications:**

**Features:**
- View all applications
- Track application status
- Update application status
- Filter by status
- Pagination support

**Application Data:**
- Student ID
- Company name
- Position/Job title
- Recruiter ID
- Status badge
- Applied date
- Action buttons

**Status Options:**
- Applied
- Interview
- Offer
- Rejected
- Withdrawn

**Filters:**
- By status (all, applied, interview, offer, rejected)

---

### 4. Payments

**Track financial transactions:**

**Two tabs:**
1. **Student Payments**
   - Student ID
   - Amount
   - Payment type
   - Status
   - Date
   - Update button

2. **Recruiter Payments**
   - Recruiter ID
   - Amount
   - Salary month (YYYY-MM)
   - Status
   - Date
   - Update button

**Payment Status:**
- Pending
- Completed
- Failed
- Refunded

**Actions:**
- Record new payment
- Update payment status
- View payment history

---

### 5. Analytics

**Performance metrics and insights:**

**Components:**
1. **Application Status Breakdown**
   - Applied count with progress bar
   - Interview count with progress bar
   - Offer count with progress bar

2. **Top Recruiters**
   - Recruiter name
   - Total applications
   - Success rate percentage

3. **Daily Applications Chart**
   - Last 7 days trend
   - Visual representation

4. **Monthly Revenue Chart**
   - Revenue trend over time
   - Profit visualization

**Metrics:**
- Success rate by status
- Applications per recruiter
- Revenue and profit trends

---

### 6. Reports

**Generate detailed reports:**

**Available Reports:**

1. **Application Report**
   - Total applications
   - Breakdown by status
   - Recruiter-wise distribution

2. **Financial Report**
   - Total revenue
   - Total paid out
   - Net profit
   - Payment counts

3. **Recruiter Performance Report**
   - Recruiter rankings
   - Success rates
   - Application counts

4. **Student Progress Report**
   - Student activity
   - Application history
   - Success metrics

**Report Features:**
- Generate on demand
- Display in modal
- Print functionality
- PDF download option

---

## 🔧 Technical Details

### Architecture

```
Admin Dashboard
├── Navigation (Sidebar)
├── Top Bar (Search, Profile)
└── Content Area
    ├── Dashboard
    ├── Users
    ├── Applications
    ├── Payments
    ├── Analytics
    └── Reports
```

### File Structure

```
admin-dashboard.html      (Main structure)
admin-styles.css          (All styling)
admin-script.js           (Logic & API calls)
```

### Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with variables
- **JavaScript (Vanilla)** - No dependencies
- **Fetch API** - Backend communication
- **LocalStorage** - Token persistence

---

## 🔐 Authentication

### Login Flow

1. User logs in via landing page
2. Token stored in localStorage
3. Admin dashboard checks for token
4. If no token → redirect to login
5. Token included in all API calls

**Header Format:**
```javascript
Authorization: Bearer <token>
```

### Security

- JWT token validation
- Role-based access control
- Protected API endpoints
- Secure password hashing (bcrypt)

---

## 🎨 UI Features

### Design Elements

1. **Color Scheme**
   - Primary Dark: #0B0B0B
   - Secondary Dark: #1A1A1A
   - Accent Blue: #00E5FF
   - Accent Orange: #FF6A00
   - Accent Teal: #00D4AA

2. **Typography**
   - Headings: Poppins (bold, 700-800)
   - Body: Inter (regular, 400-600)
   - Sizes: 0.85rem to 1.8rem

3. **Components**
   - Stat cards with hover effects
   - Status badges (colored by status)
   - Data tables with striped rows
   - Filter dropdowns
   - Modal dialogs
   - Toast notifications
   - Progress bars
   - Action buttons

4. **Interactions**
   - Smooth transitions (0.3s)
   - Hover state transforms
   - Active navigation highlighting
   - Loading indicators
   - Success/error toasts

---

## 📱 Responsive Design

### Breakpoints

| Device | Width | Layout |
|--------|-------|--------|
| Desktop | > 1200px | Full layout |
| Tablet | 768-1200px | Adjusted grids |
| Mobile | < 768px | Vertical stack |

### Mobile Features

- Responsive sidebar (horizontal tabs)
- Adjusted grid layouts
- Touch-friendly buttons
- Optimized tables

---

## 🔗 API Integration

### Endpoints Used

#### Users
```
GET  /api/users                        (List users)
POST /api/auth/register                (Create user)
PATCH /api/users/{id}/toggle-status    (Update status)
```

#### Applications
```
GET  /api/applications                 (List applications)
GET  /api/applications/{id}            (Get details)
PATCH /api/applications/{id}           (Update status)
DELETE /api/applications/{id}          (Delete)
```

#### Payments
```
GET  /api/payments/student             (List student payments)
GET  /api/payments/recruiter           (List recruiter payments)
PATCH /api/payments/{type}/{id}        (Update status)
```

#### Analytics
```
GET  /api/analytics/system             (Overall stats)
GET  /api/analytics/applications       (App stats)
GET  /api/analytics/recruiters         (Recruiter perf)
GET  /api/analytics/financial          (Financial data)
GET  /api/analytics/daily              (Daily report)
```

---

## 📊 Data Display

### Tables

**Features:**
- Sortable columns (future enhancement)
- Pagination
- Filtering
- Responsive design
- Action buttons per row

**Status Badges:**
- Color-coded by status
- Student, Applied, Interview, Offer, etc.
- Completed (green), Pending (orange), Rejected (red)

### Charts

**Implemented:**
- Status distribution chart
- Financial overview (stats)
- Progress bars for status breakdown

**Future Enhancements:**
- Line charts for trends
- Bar charts for comparisons
- Pie charts for distribution

---

## 🎯 User Workflows

### Creating a New User

1. Click "Add User" button
2. Fill form (Username, Email, Password, Role)
3. Click "Create User"
4. Success toast appears
5. User added to table

### Updating Application Status

1. Go to Applications section
2. Click "Update" on any application
3. Enter new status
4. Confirmation toast
5. Table refreshes

### Generating a Report

1. Go to Reports section
2. Click on report type button
3. Report generates and displays
4. View in modal or print/download
5. Options: Print or Download PDF

### Managing Payments

1. Go to Payments section
2. Select tab (Student/Recruiter)
3. View payment records
4. Click "Update" to change status
5. Confirm status change

---

## 🔔 Notifications

### Toast Messages

**Success:**
- User created successfully
- Payment status updated
- Data refreshed

**Error:**
- Failed to load data
- Failed to create user
- API errors

**Format:**
```javascript
showToast(message, type)  // type: 'success' | 'error' | 'info'
```

---

## 💾 State Management

### Local State (state object)

```javascript
{
    currentUser: {username, role},
    currentPage: 'dashboard',
    users: [],
    applications: [],
    payments: [],
    analytics: {}
}
```

### Persistence

- Auth token in localStorage
- State in memory during session
- Data fetched on demand

---

## 🚀 Performance Features

- **Lazy Loading**: Fetch on section switch
- **Pagination**: 10 items per page default
- **Filtering**: Client-side filtering
- **Caching**: Data stored in state
- **Optimization**: Minimal re-renders

---

## 🧪 Testing the Dashboard

### Login
1. Open `admin-dashboard.html`
2. If not authenticated, redirected to login
3. Login with admin account
4. Dashboard loads automatically

### Test Users
```
Admin Account:
Username: admin_user
Password: AdminPass123!
```

### Sample Actions

1. **View Dashboard**
   - Check stat cards load
   - Recent applications appear
   - Financial stats display

2. **Create User**
   - Click "Add User"
   - Fill form
   - Verify user in list

3. **Filter Users**
   - Select role filter
   - Verify filtering works

4. **View Analytics**
   - Check status breakdown
   - View recruiter rankings
   - See charts

5. **Generate Report**
   - Click report button
   - View generated report
   - Try print/download

---

## 🔧 Configuration

### API Base URL

Edit in `admin-script.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### Token Storage
```javascript
localStorage.getItem('authToken')
```

### Styling Variables

Edit in `admin-styles.css`:
```css
--primary-dark: #0B0B0B;
--accent-blue: #00E5FF;
/* etc */
```

---

## 📋 Features Checklist

- [x] Dashboard overview
- [x] User management
- [x] User creation/editing
- [x] User filtering
- [x] Application tracking
- [x] Payment management
- [x] Payment status updates
- [x] Analytics display
- [x] Report generation
- [x] Responsive design
- [x] Authentication
- [x] Error handling
- [x] Toast notifications
- [x] Modal dialogs
- [x] Pagination
- [x] Search functionality

---

## 🐛 Troubleshooting

### Dashboard Won't Load
- Check if logged in
- Verify API base URL
- Check browser console for errors
- Ensure token is valid

### Data Not Appearing
- Verify API is running
- Check network tab in dev tools
- Ensure authentication token
- Check API response format

### Styling Issues
- Clear browser cache
- Check CSS file is loaded
- Verify color variables
- Test in different browser

### API Errors
- Check backend is running
- Verify endpoint URLs
- Check request headers
- Review API response

---

## 📞 Support

For issues:
1. Check browser console (F12)
2. Verify API connectivity
3. Check authentication
4. Review BACKEND_README.md

---

## 🎯 Future Enhancements

- Real-time notifications
- Advanced charting library
- Bulk actions
- User preferences
- Audit logs
- Data export (CSV, Excel)
- Email integration
- Scheduled reports
- Multi-language support
- Dark mode toggle

---

**GETIVA Admin Dashboard v1.0** | Production Ready
