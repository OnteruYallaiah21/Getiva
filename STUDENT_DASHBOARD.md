# GETIVA Student Dashboard

Comprehensive job seeker portal for tracking applications and managing job search journey.

## 🎯 Overview

The Student Dashboard empowers job seekers to:
- Track all job applications in real-time
- Manage resume uploads
- Schedule and track interviews
- Monitor success metrics and progress
- Achieve career milestones

**URL**: `student-dashboard.html`

---

## 📊 Dashboard Sections

### 1. Overview (Home)

**Welcome and Quick Stats:**

**Welcome Card:**
- Personalized greeting
- Quick statistics (Total Apps, Interviews, Offers)

**Quick Actions:**
Four action cards linking to main features:
- View Applications
- Upload Resume
- Schedule Interviews
- Track Progress

**Information Cards:**
1. **Application Status**
   - Applied count
   - Interview count
   - Offer count
   - Rejected count

2. **Success Rate**
   - Animated circular progress (0-100%)
   - Visual indicator of conversion rate

3. **Latest Activity**
   - Recent applications with status
   - Company names and positions
   - Applied dates
   - Status indicators

---

### 2. Applications

**Track job applications:**

**Features:**
- Display all applications in card grid
- Filter by status (Applied, Interview, Offer, Rejected)
- Search by company name
- View application details
- Update application status

**Application Card:**
```
┌─────────────────────┐
│ Company Name   [STATUS]
│ Job Title
│
│ Applied Date   via Recruiter
│ [Details] [Update]
└─────────────────────┘
```

**Filters:**
- Status dropdown (All, Applied, Interview, Offer, Rejected)
- Search input (real-time filtering)

**Status Badges:**
- Applied (Blue)
- Interview (Orange)
- Offer (Teal)
- Rejected (Red)

**Actions:**
- Click to view full details
- Update status per application
- Modal popup for details

---

### 3. Profile

**Manage personal information:**

**Profile Form:**
- Full Name
- Email (read-only)
- Phone number
- Professional Summary

**Features:**
- Save profile changes
- Local storage persistence
- Form validation
- Cancel changes

---

### 4. Resume Management

**Upload and manage resume files:**

**Upload Area:**
- Drag-and-drop zone
- Click to browse files
- Supported formats: PDF, DOC, DOCX
- File size limit: 5MB

**Resume Information:**
- File name display
- File size
- Last updated date
- Download button
- Delete button

**Features:**
- Automatic upload to Supabase
- Public URL generation
- Download capability
- Delete with confirmation

---

### 5. Interview Schedule

**Manage interview appointments:**

**Interview Card:**
```
┌──────────────────────┐
│ Company    [TYPE]
│ 
│ 💼 Position: Role
│ 📅 Date: Scheduled Time
│
│ [Cancel]
└──────────────────────┘
```

**Schedule Interview Modal:**
- Company name
- Position
- Date & time picker
- Interview type (Phone, Video, In-Person)
- Notes textarea

**Interview Types:**
- Phone Interview
- Video Interview
- In-Person Interview

**Features:**
- Schedule new interviews
- View all scheduled interviews
- Cancel interviews
- Add notes for each interview
- Local storage persistence

---

### 6. Progress Tracking

**Monitor job search metrics:**

**Stats Summary:**
- Total Applications
- Interviews Scheduled
- Job Offers
- Success Rate (%)

**Milestones:**
Three achievement levels:
1. ✓ First Application
   - Unlocked when first app created
   
2. ✓ First Interview
   - Unlocked when first interview scheduled
   
3. ✓ Job Offer
   - Unlocked when first offer received

**Charts:**
- Applications Over Time (line chart)
- Status Distribution (pie/bar chart)

---

## 🔧 Technical Details

### Architecture

```
Student Dashboard
├── Sidebar Navigation
├── Top Bar (Notifications, Profile)
└── Content Area
    ├── Overview
    ├── Applications
    ├── Profile
    ├── Resume
    ├── Interviews
    └── Progress
```

### File Structure

```
student-dashboard.html    (Main structure)
student-styles.css        (Styling)
student-script.js         (Logic & API calls)
```

### Technology Stack

- **HTML5** - Semantic structure
- **CSS3** - Modern styling (flexbox, grid)
- **JavaScript (Vanilla)** - Pure JS, no dependencies
- **Fetch API** - Backend communication
- **LocalStorage** - Data persistence

---

## 🔐 Authentication

### Login Flow
1. User logs in via landing page
2. Token stored in localStorage
3. Dashboard checks for token
4. Redirect to login if no token

**Header Format:**
```javascript
Authorization: Bearer <token>
```

---

## 🎨 Design Highlights

### Color Scheme
- Primary Dark: #0B0B0B
- Secondary Dark: #1A1A1A
- Accent Blue: #00E5FF
- Accent Orange: #FF6A00
- Accent Teal: #00D4AA

### Typography
- Headings: Poppins (bold)
- Body: Inter (regular)
- Clear hierarchy and spacing

### Components
- Welcome card with stats
- Application cards in grid
- Status badges (color-coded)
- Modal dialogs
- Toast notifications
- Progress circles
- Action cards
- Filter controls

### Interactions
- Smooth transitions
- Hover effects
- Drag-and-drop upload
- Modal animations
- Toast notifications
- Loading states

---

## 📱 Responsive Design

### Breakpoints
| Device | Width | Changes |
|--------|-------|---------|
| Desktop | > 1200px | Full sidebar, multi-column |
| Tablet | 768-1200px | Adjusted grids |
| Mobile | < 768px | Vertical layout, tabs |

### Mobile Features
- Horizontal navigation tabs
- Single-column layout
- Touch-optimized buttons
- Responsive forms

---

## 🔗 API Integration

### Endpoints Used

```
Authentication:
POST   /api/auth/register
POST   /api/auth/login

Applications:
GET    /api/applications
GET    /api/applications/{id}
PATCH  /api/applications/{id}

Files:
POST   /api/files/resume
GET    /api/files/resume
DELETE /api/files/{path}

Analytics:
GET    /api/analytics/applications
```

### Data Persistence

**LocalStorage:**
- Auth token
- Student profile
- Scheduled interviews

**API/Database:**
- Applications
- Resume files
- User profile

---

## 📊 Data Display

### Application Cards
- Company name with status badge
- Job title
- Applied date
- Recruiter info
- Action buttons (Details, Update)

### Status Indicators
- Color-coded badges
- Applied (Blue) → Interview (Orange) → Offer (Teal)
- Rejected (Red)

### Progress Visualization
- Success rate circle (0-100%)
- Milestone checkmarks
- Stats cards
- Activity timeline

---

## 🎯 User Workflows

### 1. View Applications
1. Click "Applications" in sidebar
2. See all applications in card grid
3. Filter by status or search
4. Click card to view details

### 2. Upload Resume
1. Go to Resume section
2. Drag-and-drop file or click to browse
3. Wait for upload completion
4. View resume info and download link

### 3. Schedule Interview
1. Click "Interview Schedule"
2. Click "Schedule Interview" button
3. Fill interview details
4. Save to calendar
5. View in interview list

### 4. Track Progress
1. Go to Progress section
2. View overall statistics
3. See milestone achievements
4. Monitor success rate
5. Track application trends

### 5. Update Profile
1. Click "Profile"
2. Edit information
3. Click "Save Profile"
4. Changes persisted

---

## 💾 Data Storage

### LocalStorage
```javascript
// Auth Token
localStorage.getItem('authToken')

// Student Profile
localStorage.getItem('studentProfile')

// Scheduled Interviews
localStorage.getItem('studentInterviews')
```

### Backend Storage
- Applications
- Resume files
- Success metrics
- Analytics data

---

## 🔔 Notifications

### Toast Messages

**Success:**
- Profile saved
- Resume uploaded
- Interview scheduled

**Error:**
- Upload failed
- Network error
- Loading failure

**Info:**
- Feature coming soon

**Format:**
```javascript
showToast(message, type)  // success | error | info
```

---

## 🚀 Features

### Current Features
- ✅ Application tracking
- ✅ Application filtering and search
- ✅ Resume upload/download
- ✅ Profile management
- ✅ Interview scheduling
- ✅ Progress tracking
- ✅ Success rate calculation
- ✅ Milestone achievements
- ✅ Activity timeline
- ✅ Responsive design

### Future Enhancements
- [ ] Email notifications
- [ ] Calendar integration
- [ ] Interview reminders
- [ ] Resume templates
- [ ] Cover letter templates
- [ ] Salary tracking
- [ ] Job recommendations
- [ ] Networking tools
- [ ] Interview preparation
- [ ] Analytics charts

---

## 🧪 Testing

### Manual Testing

**Overview Section:**
1. Check welcome message loads
2. Verify stat cards show correct numbers
3. Confirm success rate calculates correctly
4. Check activity timeline displays

**Applications Section:**
1. View all applications
2. Filter by status
3. Search by company
4. Click for details
5. Update status

**Resume Upload:**
1. Drag and drop file
2. Click to browse
3. Verify upload success
4. Download resume
5. Delete resume

**Interview Scheduling:**
1. Click schedule button
2. Fill form
3. Save interview
4. View in list
5. Cancel interview

**Profile Management:**
1. Edit profile info
2. Save changes
3. Verify persistence

---

## ⚠️ Troubleshooting

### Dashboard Won't Load
- Check if logged in
- Verify API base URL
- Check browser console
- Ensure token is valid

### Data Not Appearing
- Verify API is running
- Check network requests
- Ensure authentication
- Clear localStorage

### Upload Failures
- Check file format
- Verify file size < 5MB
- Check network connection
- Verify Supabase setup

### Storage Issues
- Clear browser cache
- Check localStorage limit
- Verify API connectivity

---

## 📞 Support

For issues:
1. Check browser console (F12)
2. Verify API connectivity
3. Check authentication token
4. Review BACKEND_README.md

---

## 🎯 User Goals

**Students can:**
- ✅ Track all applications in one place
- ✅ Monitor interview opportunities
- ✅ Manage job documents (resumes)
- ✅ View success metrics
- ✅ Celebrate milestones
- ✅ Stay organized and motivated

---

## 📊 Analytics Integration

### Metrics Tracked
- Total applications
- Status distribution
- Success rate (offers / total)
- Interview count
- Activity timeline

### Visualizations
- Success rate circle
- Status breakdown cards
- Activity feed
- Milestone badges
- Statistics cards

---

## 🔐 Security & Privacy

### Authentication
- JWT token validation
- Secure token storage
- Automatic logout
- Protected API calls

### Data Privacy
- User-only access
- Local data storage
- Secure file uploads
- No data sharing

---

## 📈 Performance

### Optimization
- Lazy loading sections
- Efficient filtering (client-side)
- Minimal API calls
- Local storage caching
- Responsive images

### Loading States
- Loading indicators
- Smooth transitions
- Clear feedback
- Error messages

---

**GETIVA Student Dashboard v1.0** | Ready for Use
Modern, intuitive job search companion
