# GETIVA Recruiter Dashboard

Complete management portal for job placement professionals to manage students and track application success.

## 🎯 Overview

The Recruiter Dashboard enables recruitment professionals to:
- Manage their portfolio of students
- Create job applications on behalf of students
- Track application progress through the hiring funnel
- Monitor performance metrics and success rates
- Track earnings and payments

**URL**: `recruiter-dashboard.html`

---

## 📊 Dashboard Sections

### 1. Dashboard (Home)

**Welcome and Performance Overview:**

**Key Metrics:**
- Total Students
- Total Applications
- Interviews Scheduled
- Job Offers Received

**Visual Elements:**
- Welcome card with action button
- Success rate animated circle (0-100%)
- Monthly statistics cards
- Recent applications list

**Success Rate Calculation:**
```
Success Rate = (Offers / Total Applications) × 100%
```

**Monthly Statistics:**
- Applications created this month
- Interviews scheduled this month
- Offers received this month

---

### 2. Student Management

**Manage and track students:**

**Features:**
- View all assigned students
- Add new students to portfolio
- Track student performance
- Filter and search students

**Student Card Display:**
```
┌──────────────────────┐
│ Student Name
│ student@email.com
│
│ Apps: 12 | Interviews: 3
│ Offers: 1 | Success: 8%
│
│ [View] [Create App]
└──────────────────────┘
```

**Student Information:**
- Full name
- Email address
- Phone number
- Application count
- Interview count
- Job offers
- Success rate

**Actions:**
- View student details
- Create application for student
- Track student performance

---

### 3. Applications Management

**Create and track applications:**

**Features:**
- Create new applications
- View all applications
- Filter by status
- Search by company
- Update application status
- Pagination support

**Application Table:**
| Student | Company | Position | Status | Applied | Actions |
|---------|---------|----------|--------|---------|---------|
| ID | Name | Title | Status | Date | Update |

**Application Status:**
- Applied (Blue)
- Interview (Orange)
- Offer (Teal)
- Rejected (Red)

**Create Application Modal:**
```
- Select Student
- Company Name
- Position Title
- Job Description
- Job URL
```

---

### 4. Performance Analytics

**Track metrics and conversion:**

**Components:**

1. **Application Breakdown**
   - Applied count with progress bar
   - Interview count with progress bar
   - Offer count with progress bar

2. **Conversion Funnel**
   - Applied → Interview → Offer
   - Visual funnel representation
   - Success rate at each stage

3. **Student Performance Table**
   - Student name
   - Application count
   - Interview count
   - Success rate percentage

**Metrics Tracked:**
- Total applications created
- Interview conversion rate
- Offer conversion rate
- Success rate by student

---

### 5. Payment Management

**Track earnings and payments:**

**Payment Summary:**
- Total Earned: All money earned
- Total Paid: Completed payments
- Pending: Awaiting payment

**Payment Table:**
| Month | Amount | Status | Date |
|-------|--------|--------|------|
| YYYY-MM | $0.00 | completed | Date |

**Payment Status:**
- Pending (Orange)
- Completed (Teal)
- Failed (Red)

**Payment Breakdown:**
- Monthly salary records
- Payment history
- Status tracking
- Date of payment

---

### 6. Settings & Profile

**Manage account settings:**

**Profile Settings:**
- Name (editable)
- Email (read-only)
- Phone (editable)
- Save changes

**Account Management:**
- Change password
- Delete account
- Security settings

---

## 🏗️ Architecture

```
Recruiter Dashboard
├── Sidebar Navigation
├── Top Bar (Notifications, Profile)
└── Content Area
    ├── Dashboard
    ├── Students
    ├── Applications
    ├── Performance
    ├── Payments
    └── Settings
```

### File Structure

```
recruiter-dashboard.html    (Main structure)
recruiter-styles.css        (Styling)
recruiter-script.js         (Logic & API calls)
```

---

## 🎨 Design

### Color Scheme
- Primary Dark: #0B0B0B
- Secondary Dark: #1A1A1A
- Accent Orange: #FF6A00 (Recruiter primary)
- Accent Blue: #00E5FF
- Accent Teal: #00D4AA

### Components
- Stat cards with hover effects
- Student cards (4 columns grid)
- Application table (paginated)
- Modal dialogs for forms
- Status badges (color-coded)
- Progress bars
- Success circle visualization
- Toast notifications

### Interactions
- Smooth transitions (0.3s)
- Hover transforms
- Active navigation
- Modal animations
- Filter operations
- Search functionality

---

## 📱 Responsive Design

### Breakpoints
| Device | Width | Layout |
|--------|-------|--------|
| Desktop | > 1200px | Full sidebar |
| Tablet | 768-1200px | Adjusted grids |
| Mobile | < 768px | Vertical nav |

### Mobile Features
- Horizontal navigation tabs
- Single-column student grid
- Stacked stat cards
- Responsive tables
- Touch-friendly buttons

---

## 🔗 API Integration

### Endpoints Used

```
Applications:
POST   /api/applications
GET    /api/applications
PATCH  /api/applications/{id}

Analytics:
GET    /api/analytics/applications
GET    /api/analytics/recruiters

Payments:
GET    /api/payments/recruiter
```

### Data Flow

```
Dashboard → Load Analytics → Update Stats
         → Load Applications
         → Load Students
         
Students → Load Students List → Display Cards
        → Add New Student

Applications → Create Application → API Call
            → List Applications
            → Update Status

Performance → Load Analytics Data
           → Calculate Funnel
           → Display Stats
```

---

## 📊 Key Metrics

### Performance Indicators
- **Success Rate**: (Offers ÷ Total Applications) × 100%
- **Conversion Rate**: (Interviews ÷ Applied) × 100%
- **Offer Rate**: (Offers ÷ Interviews) × 100%

### Student Metrics
- Total applications per student
- Interview count
- Offer count
- Individual success rate

### Monthly Metrics
- Applications created this month
- Interviews scheduled
- Offers received
- Average applications per day

---

## 🧪 Testing Checklist

### Dashboard Section
- [ ] Stats load correctly
- [ ] Success rate calculates
- [ ] Recent apps display
- [ ] Monthly stats show

### Students Section
- [ ] Student cards display
- [ ] Search functionality works
- [ ] Filter options work
- [ ] Action buttons function

### Applications Section
- [ ] Table displays data
- [ ] Filter by status works
- [ ] Search works
- [ ] Create modal opens
- [ ] Application created successfully

### Performance Section
- [ ] Breakdown stats display
- [ ] Funnel visualization shows
- [ ] Progress bars animate
- [ ] Student table displays

### Payments Section
- [ ] Payment summary shows
- [ ] Payment table displays
- [ ] Status badges display

---

## 💡 User Workflows

### Creating Application
1. Click "New Application" button
2. Select student from dropdown
3. Enter company name
4. Enter position title
5. (Optional) Add job description and URL
6. Click "Create Application"
7. Confirmation toast appears
8. Return to applications list

### Adding Student
1. Click "Add Student" button
2. Enter full name
3. Enter email
4. (Optional) Enter phone
5. Click "Add Student"
6. Student added to portfolio
7. Can now create applications

### Tracking Performance
1. Go to Performance section
2. View breakdown by status
3. See conversion funnel
4. Check student performance
5. Identify top performers

### Monitoring Payments
1. Go to Payments section
2. View summary (Earned, Paid, Pending)
3. Review payment history
4. Check payment status

---

## 🔐 Authentication

### Login Flow
1. Authenticate via landing page
2. Token stored in localStorage
3. Dashboard verifies token
4. Redirect to login if invalid

**Protected Endpoints:**
- Requires Bearer token
- Token in Authorization header
- Auto-logout on token expiry

---

## 📈 Performance Metrics

### Dashboard
- Total students managed
- Total applications created
- Success rate (%)
- Monthly activity

### Student Card
- Name & contact
- Application count
- Interview count
- Offers received
- Success rate

### Application Funnel
- Applied: All applications
- Interview: Moved to interview
- Offer: Received job offer
- Conversion rates between stages

---

## 🚀 Features

### Current Features
- [x] Dashboard with metrics
- [x] Student management
- [x] Application creation
- [x] Application tracking
- [x] Performance analytics
- [x] Conversion funnel
- [x] Payment tracking
- [x] Settings management
- [x] Search and filter
- [x] Responsive design

### Future Enhancements
- [ ] Email notifications
- [ ] Batch application creation
- [ ] Student resume preview
- [ ] Interview scheduling integration
- [ ] Salary/commission tracking
- [ ] Performance reports (PDF)
- [ ] Team management
- [ ] Commission calculations
- [ ] Export data (CSV, Excel)
- [ ] Advanced analytics

---

## 📊 Dashboard Statistics

**Example Metrics:**
- Students: 5-50
- Applications: 20-500+
- Success Rate: 8-20%
- Offers: 2-50+
- Monthly Target: 50-100 applications

---

## 🎯 Success Indicators

**Good Performance:**
- ✅ Success rate > 10%
- ✅ Interview rate > 20%
- ✅ Consistent monthly applications
- ✅ High student retention

**Areas to Monitor:**
- Low interview conversion
- Declining success rate
- Student drop-offs
- Payment delays

---

## 🔧 Configuration

### API Base URL
Edit in `recruiter-script.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### Token Storage
```javascript
localStorage.getItem('authToken')
```

### Settings Storage
```javascript
localStorage.getItem('recruiterSettings')
```

---

## ⚠️ Troubleshooting

### Dashboard Won't Load
- Check internet connection
- Verify API is running
- Check token validity
- Clear browser cache

### Data Not Appearing
- Verify API endpoints
- Check authentication token
- Review network requests
- Check API response format

### Filters Not Working
- Clear search/filter values
- Refresh page
- Check data exists
- Verify filter logic

### Modal Not Opening
- Check browser console
- Verify JavaScript loaded
- Check element IDs
- Test in different browser

---

## 📞 Support

For issues:
1. Check browser console (F12)
2. Verify API connectivity
3. Check authentication
4. Review BACKEND_README.md
5. Check API response format

---

## 📋 User Roles Comparison

| Feature | Recruiter | Admin | Student |
|---------|-----------|-------|---------|
| Create Apps | ✅ | ✅ | ❌ |
| View Students | ✅ | ✅ | ❌ |
| Track Performance | ✅ | ✅ | ✅ |
| View Payments | ✅ | ✅ | ❌ |
| Manage Users | ❌ | ✅ | ❌ |
| System Settings | ❌ | ✅ | ❌ |

---

## 🎨 Customization

### Change Accent Color
Edit `recruiter-styles.css`:
```css
--accent-orange: #FF6A00;  /* Change this */
```

### Modify Success Rate Formula
Edit `recruiter-script.js`:
```javascript
const successRate = Math.round((stats.offer_count / total) * 100);
```

### Update Stat Cards
Edit HTML or modify dashboard data display

---

**GETIVA Recruiter Dashboard v1.0** | Production Ready
Professional job placement management tool
