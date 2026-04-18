/* ============================================
   GETIVA Student Dashboard JavaScript
   ============================================ */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';
let authToken = localStorage.getItem('authToken');

// State management
const state = {
    currentUser: null,
    currentSection: 'overview',
    applications: [],
    interviews: [],
    profile: null,
    resume: null,
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Check authentication
    if (!authToken) {
        redirectToLogin();
        return;
    }

    // Load current user
    await loadCurrentUser();

    // Setup event listeners
    setupEventListeners();

    // Load initial data
    await loadOverviewData();
}

// ============================================
// AUTHENTICATION
// ============================================

async function loadCurrentUser() {
    try {
        state.currentUser = {
            id: 'student-id',
            name: 'Student Name',
            email: 'student@example.com',
        };
        document.getElementById('userName').textContent = state.currentUser.name;
        document.getElementById('welcomeName').textContent = state.currentUser.name.split(' ')[0];
    } catch (error) {
        console.error('Failed to load user:', error);
        redirectToLogin();
    }
}

function redirectToLogin() {
    window.location.href = 'index.html';
}

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Sidebar navigation
    document.querySelectorAll('.nav-link').forEach((link) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            switchSection(section);
        });
    });

    // Quick action links
    document.querySelectorAll('.action-card').forEach((card) => {
        card.addEventListener('click', (e) => {
            e.preventDefault();
            const section = card.dataset.section;
            switchSection(section);
        });
    });

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Resume upload
    const uploadArea = document.getElementById('uploadArea');
    const resumeFile = document.getElementById('resumeFile');

    uploadArea?.addEventListener('click', () => resumeFile.click());
    uploadArea?.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--accent-blue)';
    });
    uploadArea?.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border-color)';
    });
    uploadArea?.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        if (e.dataTransfer.files.length > 0) {
            handleResumeUpload(e.dataTransfer.files[0]);
        }
    });

    resumeFile?.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleResumeUpload(e.target.files[0]);
        }
    });

    // Profile form
    document.getElementById('profileForm')?.addEventListener('submit', handleProfileSave);

    // Interview form
    document.getElementById('interviewForm')?.addEventListener('submit', handleInterviewSchedule);

    // Modal close buttons
    document.querySelectorAll('.close-btn').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').classList.remove('active');
        });
    });

    // Applications filter
    document.getElementById('statusFilter')?.addEventListener('change', filterApplications);
    document.getElementById('searchApplications')?.addEventListener('input', filterApplications);
}

// ============================================
// NAVIGATION
// ============================================

function switchSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach((sec) => sec.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach((link) => link.classList.remove('active'));

    // Show selected section
    const section = document.getElementById(`${sectionName}-section`);
    if (section) {
        section.classList.add('active');
    }

    // Update nav link
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // Update page title
    const titles = {
        overview: 'Overview',
        applications: 'My Applications',
        profile: 'My Profile',
        resume: 'Resume Management',
        interviews: 'Interview Schedule',
        progress: 'Your Progress',
    };
    document.getElementById('pageTitle').textContent = titles[sectionName] || 'Overview';

    state.currentSection = sectionName;

    // Load section data
    loadSectionData(sectionName);
}

// ============================================
// DATA LOADING
// ============================================

async function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'overview':
            await loadOverviewData();
            break;
        case 'applications':
            await loadApplicationsData();
            break;
        case 'profile':
            await loadProfileData();
            break;
        case 'resume':
            await loadResumeData();
            break;
        case 'interviews':
            await loadInterviewsData();
            break;
        case 'progress':
            await loadProgressData();
            break;
    }
}

async function loadOverviewData() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/applications`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const stats = await response.json();

        // Update stat cards
        const total = stats.total_applications || 1;
        document.getElementById('totalApps').textContent = total;
        document.getElementById('interviewCount').textContent = stats.interview_count;
        document.getElementById('offerCount').textContent = stats.offer_count;

        // Update status breakdown
        document.getElementById('appliedCount').textContent = stats.applied_count;
        document.getElementById('interviewStatusCount').textContent = stats.interview_count;
        document.getElementById('offerStatusCount').textContent = stats.offer_count;
        document.getElementById('rejectedCount').textContent = stats.rejected_count;

        // Update success rate
        const successRate = stats.total_applications > 0
            ? Math.round((stats.offer_count / stats.total_applications) * 100)
            : 0;
        document.getElementById('successRate').textContent = successRate;
        updateSuccessCircle(successRate);

        // Load applications for activity
        await loadApplicationsData();
    } catch (error) {
        console.error('Failed to load overview:', error);
        showToast('Failed to load overview data', 'error');
    }
}

async function loadApplicationsData() {
    try {
        const response = await fetch(`${API_BASE_URL}/applications`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        state.applications = data.items || [];

        // For overview section
        if (state.currentSection === 'overview') {
            displayRecentActivity();
        }
        // For applications section
        else {
            displayApplications(state.applications);
        }
    } catch (error) {
        console.error('Failed to load applications:', error);
    }
}

function displayRecentActivity() {
    const container = document.getElementById('activityList');
    if (!container) return;

    container.innerHTML = '';

    if (state.applications.length === 0) {
        container.innerHTML = '<p class="empty">No applications yet. Start applying to jobs!</p>';
        return;
    }

    state.applications.slice(0, 5).forEach((app) => {
        const icons = {
            applied: '📝',
            interview: '📞',
            offer: '🎉',
            rejected: '❌',
        };

        const div = document.createElement('div');
        div.className = 'activity-item';
        div.innerHTML = `
            <div class="activity-icon">${icons[app.status] || '📝'}</div>
            <div class="activity-details">
                <div class="activity-company">${app.company_name}</div>
                <div class="activity-status">${app.job_title} - <strong>${app.status}</strong></div>
                <div class="activity-date">${new Date(app.applied_date).toLocaleDateString()}</div>
            </div>
        `;
        container.appendChild(div);
    });
}

function displayApplications(applications) {
    const grid = document.getElementById('applicationsGrid');
    if (!grid) return;

    grid.innerHTML = '';

    if (applications.length === 0) {
        grid.innerHTML = '<div class="empty">No applications found</div>';
        return;
    }

    applications.forEach((app) => {
        const card = document.createElement('div');
        card.className = 'application-card';
        card.innerHTML = `
            <div class="app-header">
                <div>
                    <div class="company-name">${app.company_name}</div>
                    <div class="job-title">${app.job_title}</div>
                </div>
                <span class="app-status status-${app.status}">${app.status}</span>
            </div>
            <div class="app-meta">
                <span>${new Date(app.applied_date).toLocaleDateString()}</span>
                <span>via ${app.recruiter_id.substring(0, 8)}</span>
            </div>
            <div class="app-footer">
                <button class="app-btn" onclick="viewApplicationDetails('${app.id}')">Details</button>
                <button class="app-btn" onclick="editApplicationStatus('${app.id}')">Update</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

async function loadProfileData() {
    // Populate profile form with current data
    document.getElementById('fullName').value = state.currentUser?.name || '';
    document.getElementById('profileEmail').value = state.currentUser?.email || '';
}

async function loadResumeData() {
    // Check if resume exists
    try {
        const response = await fetch(`${API_BASE_URL}/files/resume`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (response.ok) {
            const data = await response.json();
            if (data.resume_url) {
                displayResumeInfo(data.resume_url);
            }
        }
    } catch (error) {
        console.error('Failed to load resume:', error);
    }
}

function displayResumeInfo(url) {
    const uploadArea = document.getElementById('uploadArea');
    const resumeInfo = document.getElementById('resumeInfo');

    if (uploadArea) uploadArea.style.display = 'none';
    if (resumeInfo) resumeInfo.style.display = 'block';

    document.getElementById('resumeName').textContent = url.split('/').pop();
    document.getElementById('downloadResume').href = url;
}

async function loadInterviewsData() {
    // Load interviews from local storage or API
    const interviews = JSON.parse(localStorage.getItem('studentInterviews') || '[]');
    displayInterviews(interviews);
}

function displayInterviews(interviews) {
    const container = document.getElementById('interviewsList');
    if (!container) return;

    container.innerHTML = '';

    if (interviews.length === 0) {
        container.innerHTML = '<div class="empty">No scheduled interviews</div>';
        return;
    }

    interviews.forEach((interview, index) => {
        const card = document.createElement('div');
        card.className = 'interview-card';
        card.innerHTML = `
            <div class="interview-header">
                <div>
                    <div class="interview-company">${interview.company}</div>
                </div>
                <span class="interview-type">${interview.type}</span>
            </div>
            <div class="interview-details">
                <div class="detail-item">
                    <div class="detail-icon">💼</div>
                    <div class="detail-content">
                        <div class="detail-label">Position</div>
                        <div class="detail-value">${interview.position}</div>
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-icon">📅</div>
                    <div class="detail-content">
                        <div class="detail-label">Date & Time</div>
                        <div class="detail-value">${new Date(interview.dateTime).toLocaleString()}</div>
                    </div>
                </div>
            </div>
            ${interview.notes ? `<div class="interview-notes"><strong>Notes:</strong> ${interview.notes}</div>` : ''}
            <div class="app-footer" style="margin-top: 1rem;">
                <button class="app-btn" onclick="deleteInterview(${index})">Cancel</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function loadProgressData() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/applications`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const stats = await response.json();

        // Update stats
        document.getElementById('totalApplications').textContent = stats.total_applications;
        document.getElementById('totalInterviews').textContent = stats.interview_count;
        document.getElementById('totalOffers').textContent = stats.offer_count;

        const successRate = stats.total_applications > 0
            ? Math.round((stats.offer_count / stats.total_applications) * 100)
            : 0;
        document.getElementById('displaySuccessRate').textContent = successRate + '%';

        // Unlock milestones
        if (stats.total_applications > 0) {
            document.getElementById('milestone1').classList.add('unlocked');
        }
        if (stats.interview_count > 0) {
            document.getElementById('milestone2').classList.add('unlocked');
        }
        if (stats.offer_count > 0) {
            document.getElementById('milestone3').classList.add('unlocked');
        }
    } catch (error) {
        console.error('Failed to load progress:', error);
    }
}

// ============================================
// USER INTERACTIONS
// ============================================

function filterApplications() {
    const status = document.getElementById('statusFilter').value;
    const search = document.getElementById('searchApplications').value.toLowerCase();

    let filtered = state.applications;

    if (status) {
        filtered = filtered.filter((app) => app.status === status);
    }

    if (search) {
        filtered = filtered.filter((app) =>
            app.company_name.toLowerCase().includes(search)
        );
    }

    displayApplications(filtered);
}

function viewApplicationDetails(appId) {
    const app = state.applications.find((a) => a.id === appId);
    if (!app) return;

    document.getElementById('modalCompanyName').textContent = app.company_name;
    document.getElementById('applicationDetails').innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
                <label style="font-weight: 600; color: var(--text-secondary);">Position</label>
                <p>${app.job_title}</p>
            </div>
            <div>
                <label style="font-weight: 600; color: var(--text-secondary);">Status</label>
                <p><span class="app-status status-${app.status}">${app.status}</span></p>
            </div>
            <div>
                <label style="font-weight: 600; color: var(--text-secondary);">Applied Date</label>
                <p>${new Date(app.applied_date).toLocaleDateString()}</p>
            </div>
            ${app.job_description ? `
                <div>
                    <label style="font-weight: 600; color: var(--text-secondary);">Job Description</label>
                    <p>${app.job_description}</p>
                </div>
            ` : ''}
            ${app.notes ? `
                <div>
                    <label style="font-weight: 600; color: var(--text-secondary);">Notes</label>
                    <p>${app.notes}</p>
                </div>
            ` : ''}
        </div>
    `;
    document.getElementById('applicationModal').classList.add('active');
}

function editApplicationStatus(appId) {
    const newStatus = prompt('Enter new status (applied, interview, offer, rejected):');
    if (!newStatus) return;

    // Show confirmation toast
    showToast('Status update feature coming soon', 'info');
}

async function handleResumeUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/files/resume`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${authToken}` },
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            displayResumeInfo(data.url);
            showToast('Resume uploaded successfully', 'success');
        } else {
            showToast('Failed to upload resume', 'error');
        }
    } catch (error) {
        console.error('Error uploading resume:', error);
        showToast('Error uploading resume', 'error');
    }
}

function deleteResume() {
    if (confirm('Are you sure you want to delete your resume?')) {
        const uploadArea = document.getElementById('uploadArea');
        const resumeInfo = document.getElementById('resumeInfo');

        uploadArea.style.display = 'flex';
        resumeInfo.style.display = 'none';

        showToast('Resume deleted', 'success');
    }
}

async function handleProfileSave(e) {
    e.preventDefault();

    const profile = {
        fullName: document.getElementById('fullName').value,
        phone: document.getElementById('phone').value,
        summary: document.getElementById('summary').value,
    };

    // Save to local storage for now
    localStorage.setItem('studentProfile', JSON.stringify(profile));
    showToast('Profile saved successfully', 'success');
}

function resetProfileForm() {
    document.getElementById('profileForm').reset();
}

function openInterviewModal() {
    document.getElementById('interviewModal').classList.add('active');
}

function closeInterviewModal() {
    document.getElementById('interviewModal').classList.remove('active');
    document.getElementById('interviewForm').reset();
}

async function handleInterviewSchedule(e) {
    e.preventDefault();

    const interview = {
        company: document.getElementById('interviewCompany').value,
        position: document.getElementById('interviewPosition').value,
        dateTime: document.getElementById('interviewDateTime').value,
        type: document.getElementById('interviewType').value,
        notes: document.getElementById('interviewNotes').value,
    };

    // Save to local storage
    const interviews = JSON.parse(localStorage.getItem('studentInterviews') || '[]');
    interviews.push(interview);
    localStorage.setItem('studentInterviews', JSON.stringify(interviews));

    showToast('Interview scheduled successfully', 'success');
    closeInterviewModal();
    await loadInterviewsData();
}

function deleteInterview(index) {
    if (confirm('Are you sure you want to cancel this interview?')) {
        const interviews = JSON.parse(localStorage.getItem('studentInterviews') || '[]');
        interviews.splice(index, 1);
        localStorage.setItem('studentInterviews', JSON.stringify(interviews));

        showToast('Interview cancelled', 'success');
        loadInterviewsData();
    }
}

// ============================================
// UTILITIES
// ============================================

function updateSuccessCircle(percentage) {
    const circumference = 282.7;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;
    const circle = document.getElementById('successCircle');
    if (circle) {
        circle.style.strokeDashoffset = strokeDashoffset;
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function logout() {
    localStorage.removeItem('authToken');
    window.location.href = 'index.html';
}

// Handle modal close on background click
document.querySelectorAll('.modal').forEach((modal) => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});
