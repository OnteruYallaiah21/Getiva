/* ============================================
   GETIVA Recruiter Dashboard JavaScript
   ============================================ */

// Configuration
const API_BASE_URL =
    (typeof localStorage !== 'undefined' && localStorage.getItem('apiBaseUrl')) ||
    `${window.location.origin}/api`;
let authToken = localStorage.getItem('authToken');

// State management
const state = {
    currentUser: null,
    currentSection: 'dashboard',
    students: [],
    applications: [],
    payments: [],
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    if (!authToken) {
        redirectToLogin();
        return;
    }

    await loadCurrentUser();
    setupEventListeners();
    await loadDashboardData();
}

// ============================================
// AUTHENTICATION
// ============================================

async function loadCurrentUser() {
    try {
        const r = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        if (r.status === 401) {
            redirectToLogin();
            return;
        }
        if (!r.ok) {
            throw new Error('Could not load profile');
        }
        const u = await r.json();

        if (u.role !== 'recruiter') {
            localStorage.setItem('userRole', u.role);
            if (u.role === 'student') {
                window.location.href = 'student-dashboard.html';
            } else if (u.role === 'admin') {
                window.location.href = 'admin-dashboard.html';
            } else {
                window.location.href = 'index.html';
            }
            return;
        }

        if (u.is_temp_password) {
            localStorage.setItem('mustChangePassword', 'true');
            window.location.href = 'change-password.html';
            return;
        }

        state.currentUser = u;
        const display = u.username || 'Recruiter';
        document.getElementById('userName').textContent = display;
        document.getElementById('recruiterGreeting').textContent = display.split(/[\s@]+/)[0];
    } catch (error) {
        console.error('Failed to load user:', error);
        redirectToLogin();
    }
}

function redirectToLogin() {
    window.location.href = 'login.html';
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

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Modal close buttons
    document.querySelectorAll('.close-btn').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').classList.remove('active');
        });
    });

    // Forms
    document.getElementById('applicationForm')?.addEventListener('submit', handleCreateApplication);
    document.getElementById('settingsForm')?.addEventListener('submit', handleSettingsSave);

    // Filters
    document.getElementById('searchStudents')?.addEventListener('input', filterStudents);
    document.getElementById('searchApplications')?.addEventListener('input', filterApplications);
    document.getElementById('appStatusFilter')?.addEventListener('change', filterApplications);
}

// ============================================
// NAVIGATION
// ============================================

function switchSection(sectionName) {
    document.querySelectorAll('.section').forEach((sec) => sec.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach((link) => link.classList.remove('active'));

    const section = document.getElementById(`${sectionName}-section`);
    if (section) {
        section.classList.add('active');
    }

    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    const titles = {
        dashboard: 'Dashboard',
        students: 'My Students',
        applications: 'Applications',
        performance: 'Performance',
        payments: 'Payments',
        settings: 'Settings',
    };
    document.getElementById('pageTitle').textContent = titles[sectionName] || 'Dashboard';

    state.currentSection = sectionName;
    loadSectionData(sectionName);
}

async function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'dashboard':
            await loadDashboardData();
            break;
        case 'students':
            await loadStudentsData();
            break;
        case 'applications':
            await loadApplicationsData();
            break;
        case 'performance':
            await loadPerformanceData();
            break;
        case 'payments':
            await loadPaymentsData();
            break;
        case 'settings':
            await loadSettingsData();
            break;
    }
}

// ============================================
// DATA LOADING
// ============================================

async function fetchRecruiterApplicationItems(perPage = 200) {
    const response = await fetch(
        `${API_BASE_URL}/applications?page=1&per_page=${perPage}`,
        { headers: { Authorization: `Bearer ${authToken}` } },
    );
    if (response.status === 401) {
        redirectToLogin();
        return [];
    }
    if (!response.ok) {
        return [];
    }
    const data = await response.json();
    return data.items || [];
}

function renderRecentApplicationsFromItems(items) {
    const container = document.getElementById('recentApps');
    if (!container) return;
    container.innerHTML = '';
    if (!items.length) {
        container.innerHTML = '<p class="empty">No applications yet</p>';
        return;
    }
    items.slice(0, 5).forEach((app) => {
        const div = document.createElement('div');
        div.className = 'recent-app-item';
        const resumeUrl = resolveApplicationResumeUrl(app);
        const resumePart = resumeUrl
            ? ` • <button type="button" class="resume-inline-link" onclick="viewApplicationResume('${app.id}')">Resume</button>`
            : '';
        div.innerHTML = `
                <strong>${app.company_name}</strong>
                <span>${app.job_title} • ${formatDateTime(app.applied_date)}${resumePart}</span>
            `;
        container.appendChild(div);
    });
}

/** Count applications whose applied_date falls in the current calendar month (DB-backed). */
function updateDashboardMonthStatsFromApplications(items) {
    const now = new Date();
    const y = now.getFullYear();
    const m = now.getMonth();
    let monthApps = 0;
    let monthInterviews = 0;
    let monthOffers = 0;
    for (const app of items) {
        const d = new Date(app.applied_date);
        if (d.getFullYear() !== y || d.getMonth() !== m) continue;
        monthApps += 1;
        if (app.status === 'interview') monthInterviews += 1;
        if (app.status === 'offer') monthOffers += 1;
    }
    const elA = document.getElementById('monthApps');
    const elI = document.getElementById('monthInterviews');
    const elO = document.getElementById('monthOffers');
    if (elA) elA.textContent = monthApps;
    if (elI) elI.textContent = monthInterviews;
    if (elO) elO.textContent = monthOffers;
}

function enrichStudentsApplicationCounts(applicationItems) {
    const counts = {};
    for (const s of state.students) {
        counts[s.id] = { applications: 0, interviews: 0, offers: 0 };
    }
    for (const app of applicationItems) {
        const sid = app.student_id;
        if (!counts[sid]) continue;
        counts[sid].applications += 1;
        if (app.status === 'interview') counts[sid].interviews += 1;
        if (app.status === 'offer') counts[sid].offers += 1;
    }
    state.students = state.students.map((s) => ({
        ...s,
        ...counts[s.id],
    }));
}

async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/applications`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        if (!response.ok) {
            showToast('Failed to load dashboard stats', 'error');
            return;
        }
        const stats = await response.json();

        const total = stats.total_applications || 1;
        document.getElementById('totalApplications').textContent = stats.total_applications;
        document.getElementById('interviewCount').textContent = stats.interview_count;
        document.getElementById('offerCount').textContent = stats.offer_count;

        const successRate = Math.round((stats.offer_count / total) * 100);
        document.getElementById('successRate').textContent = successRate;
        updateSuccessCircle(successRate);

        await loadStudentsData();
        const appItems = await fetchRecruiterApplicationItems(250);
        state.applications = appItems;
        updateDashboardMonthStatsFromApplications(appItems);
        renderRecentApplicationsFromItems(appItems);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showToast('Failed to load dashboard', 'error');
    }
}

async function loadRecentApplications() {
    try {
        const items = await fetchRecruiterApplicationItems(50);
        renderRecentApplicationsFromItems(items);
    } catch (error) {
        console.error('Failed to load recent applications:', error);
    }
}

async function loadStudentsData() {
    try {
        const response = await fetch(`${API_BASE_URL}/students`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        if (response.status === 401) {
            redirectToLogin();
            return;
        }
        if (!response.ok) {
            let msg = 'Could not load students';
            try {
                const err = await response.json();
                msg = formatApiDetail(err.detail) || msg;
            } catch (_) {
                /* ignore */
            }
            showToast(msg, 'error');
            state.students = [];
        } else {
            const data = await response.json();
            state.students = (Array.isArray(data) ? data : []).map((s) => ({
                id: s.id,
                name: s.full_name,
                username: s.username,
                email: s.email || '',
                resume_url: s.resume_url || '',
                applications: 0,
                interviews: 0,
                offers: 0,
            }));
        }

        const appsForCounts =
            state.applications.length > 0 ? state.applications : await fetchRecruiterApplicationItems(250);
        if (!state.applications.length) {
            state.applications = appsForCounts;
        }
        enrichStudentsApplicationCounts(appsForCounts);

        if (state.currentSection === 'dashboard') {
            const el = document.getElementById('totalStudents');
            if (el) el.textContent = state.students.length;
        } else {
            displayStudents(state.students);
        }
    } catch (error) {
        console.error('Failed to load students:', error);
        state.students = [];
        showToast('Failed to load students', 'error');
    }
}

function displayStudents(students) {
    const grid = document.getElementById('studentsGrid');
    if (!grid) return;

    grid.innerHTML = '';

    if (students.length === 0) {
        grid.innerHTML = '<div class="empty">No students found</div>';
        return;
    }

    students.forEach((student) => {
        const card = document.createElement('div');
        card.className = 'student-card';
        card.innerHTML = `
            <div class="student-header">
                <div class="student-name">${student.name}</div>
                <div class="student-email">${student.email}${student.username ? ` · @${student.username}` : ''}</div>
            </div>
            <div class="student-stats">
                <div class="stat-mini">
                    <div class="stat-mini-label">Apps</div>
                    <div class="stat-mini-value">${student.applications}</div>
                </div>
                <div class="stat-mini">
                    <div class="stat-mini-label">Interviews</div>
                    <div class="stat-mini-value">${student.interviews}</div>
                </div>
                <div class="stat-mini">
                    <div class="stat-mini-label">Offers</div>
                    <div class="stat-mini-value">${student.offers}</div>
                </div>
                <div class="stat-mini">
                    <div class="stat-mini-label">Success</div>
                    <div class="stat-mini-value">${student.applications > 0 ? Math.round((student.offers / student.applications) * 100) : 0}%</div>
                </div>
            </div>
            <div class="student-actions">
                <button onclick="viewStudentDetail('${student.id}')">View</button>
                <button onclick="createAppForStudent('${student.id}')">Apply</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

async function loadApplicationsData() {
    try {
        await loadStudentsData();
        const response = await fetch(`${API_BASE_URL}/applications`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        state.applications = data.items || [];
        displayApplicationsTable(state.applications);
    } catch (error) {
        console.error('Failed to load applications:', error);
    }
}

function resolveApplicationResumeUrl(app) {
    const direct = (app.resume_url || '').trim();
    if (direct) return direct;
    const student = state.students.find((s) => s.id === app.student_id);
    return (student?.resume_url || '').trim();
}

function displayApplicationsTable(applications) {
    const tbody = document.getElementById('applicationsTable');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (applications.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty">No applications</td></tr>';
        return;
    }

    applications.forEach((app) => {
        const resumeUrl = resolveApplicationResumeUrl(app);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${app.student_id.substring(0, 8)}</td>
            <td>${app.company_name}</td>
            <td>${app.job_title}</td>
            <td><span class="status-badge status-${app.status}">${app.status}</span></td>
            <td>${typeof formatDateTime === 'function' ? formatDateTime(app.applied_date) : new Date(app.applied_date).toLocaleString('en-US')}</td>
            <td>${buildResumeLinksHtml(resumeUrl, resumeUrl ? app.id : null)}</td>
            <td>
                <button class="action-btn" onclick="updateAppStatus('${app.id}')">Update</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function loadPerformanceData() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/applications`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        if (!response.ok) {
            showToast('Failed to load performance', 'error');
            return;
        }
        const stats = await response.json();

        const total = stats.total_applications || 1;
        document.getElementById('appliedCount').textContent = stats.applied_count;
        document.getElementById('appliedProgress').style.width = `${(stats.applied_count / total) * 100}%`;

        document.getElementById('interviewCount2').textContent = stats.interview_count;
        document.getElementById('interviewProgress').style.width = `${(stats.interview_count / total) * 100}%`;

        document.getElementById('offerCount2').textContent = stats.offer_count;
        document.getElementById('offerProgress').style.width = `${(stats.offer_count / total) * 100}%`;

        document.getElementById('funnelApplied').textContent = stats.applied_count;
        document.getElementById('funnelInterview').textContent = stats.interview_count;
        document.getElementById('funnelOffer').textContent = stats.offer_count;

        if (!state.students.length) {
            await loadStudentsData();
        } else {
            const apps =
                state.applications.length > 0 ? state.applications : await fetchRecruiterApplicationItems(250);
            if (!state.applications.length) state.applications = apps;
            enrichStudentsApplicationCounts(apps);
        }
        displayStudentPerformance(state.students);
    } catch (error) {
        console.error('Failed to load performance:', error);
    }
}

function displayStudentPerformance(students) {
    const tbody = document.getElementById('studentPerformanceTable');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!students.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty">No students in directory</td></tr>';
        return;
    }

    students.forEach((student) => {
        const successRate = student.applications > 0 ? Math.round((student.offers / student.applications) * 100) : 0;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.name}</td>
            <td>${student.applications}</td>
            <td>${student.interviews}</td>
            <td>${successRate}%</td>
        `;
        tbody.appendChild(row);
    });
}

async function loadPaymentsData() {
    try {
        const response = await fetch(`${API_BASE_URL}/payments/recruiter?page=1&per_page=100`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        if (response.status === 401) {
            redirectToLogin();
            return;
        }
        if (!response.ok) {
            let msg = 'Could not load payments';
            try {
                const err = await response.json();
                msg = formatApiDetail(err.detail) || msg;
            } catch (_) {
                /* ignore */
            }
            showToast(msg, 'error');
            state.payments = [];
            document.getElementById('totalEarned').textContent = '$0.00';
            document.getElementById('totalPaid').textContent = '$0.00';
            document.getElementById('totalPending').textContent = '$0.00';
            displayPaymentsTable([]);
            return;
        }

        const data = await response.json();
        state.payments = data.items || [];

        const totalEarned = state.payments.reduce((sum, p) => sum + Number(p.amount), 0);
        const totalPaid = state.payments
            .filter((p) => p.status === 'completed')
            .reduce((sum, p) => sum + Number(p.amount), 0);
        const totalPending = state.payments
            .filter((p) => p.status === 'pending')
            .reduce((sum, p) => sum + Number(p.amount), 0);

        document.getElementById('totalEarned').textContent = `$${totalEarned.toFixed(2)}`;
        document.getElementById('totalPaid').textContent = `$${totalPaid.toFixed(2)}`;
        document.getElementById('totalPending').textContent = `$${totalPending.toFixed(2)}`;

        displayPaymentsTable(state.payments);
    } catch (error) {
        console.error('Failed to load payments:', error);
        state.payments = [];
        showToast('Failed to load payments', 'error');
        displayPaymentsTable([]);
    }
}

function displayPaymentsTable(payments) {
    const tbody = document.getElementById('paymentsTable');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!payments.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty">No payment records yet</td></tr>';
        return;
    }

    payments.forEach((payment) => {
        const row = document.createElement('tr');
        const status = payment.status || '';
        row.innerHTML = `
            <td>${payment.salary_month}</td>
            <td>$${Number(payment.amount).toFixed(2)}</td>
            <td><span class="status-badge status-${status}">${status}</span></td>
            <td>${formatDateTime(payment.payment_date)}</td>
        `;
        tbody.appendChild(row);
    });
}

async function loadSettingsData() {
    document.getElementById('settingsName').value = state.currentUser?.username || '';
    document.getElementById('settingsEmail').value = state.currentUser?.email || '';
}

// ============================================
// USER INTERACTIONS
// ============================================

async function openCreateApplicationModal(preselectStudentId = null) {
    await loadStudentsData();
    const group = document.getElementById('studentSelectGroup');
    const select = document.getElementById('studentSelect');
    select.innerHTML = '<option value="">-- Choose student --</option>';

    state.students.forEach((student) => {
        const option = document.createElement('option');
        option.value = student.id;
        const uname = student.username ? ` (@${student.username})` : '';
        option.textContent = `${student.name}${uname}`;
        select.appendChild(option);
    });

    if (state.students.length > 1) {
        group.hidden = false;
        select.required = true;
        if (preselectStudentId && state.students.some((s) => s.id === preselectStudentId)) {
            select.value = preselectStudentId;
        } else {
            select.value = '';
        }
    } else {
        group.hidden = true;
        select.required = false;
        select.value = '';
    }

    document.getElementById('createApplicationModal').classList.add('active');
}

function closeCreateApplicationModal() {
    document.getElementById('createApplicationModal').classList.remove('active');
    document.getElementById('applicationForm').reset();
}

async function handleCreateApplication(e) {
    e.preventDefault();

    const company = document.getElementById('companyName').value.trim();
    const jobDescription = document.getElementById('jobDescription').value.trim();
    if (!company) {
        showToast('Please enter the company name.', 'error');
        return;
    }
    if (!jobDescription) {
        showToast('Please enter the job description.', 'error');
        return;
    }

    if (!state.students.length) {
        showToast('No students are available. Ask an administrator to add a student account.', 'error');
        return;
    }

    let studentId = null;
    if (state.students.length === 1) {
        studentId = state.students[0].id;
    } else {
        studentId = document.getElementById('studentSelect').value;
        if (!studentId) {
            showToast('Please select which student this application is for.', 'error');
            return;
        }
    }

    const fileInput = document.getElementById('applicationResume');
    const file = fileInput?.files?.[0];
    if (!file) {
        showToast('Please upload a file for this application.', 'error');
        return;
    }

    let resume_url;
    try {
        const fd = new FormData();
        fd.append('file', file);
        fd.append('student_id', studentId);
        const up = await fetch(`${API_BASE_URL}/files/resume`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${authToken}` },
            body: fd,
        });
        if (!up.ok) {
            let msg = 'Resume upload failed';
            try {
                const err = await up.json();
                msg = formatApiDetail(err.detail) || msg;
            } catch (_) {
                /* ignore */
            }
            showToast(msg, 'error');
            return;
        }
        const uploaded = await up.json();
        resume_url = uploaded.url;
    } catch (error) {
        console.error('Resume upload error:', error);
        showToast('Resume upload failed', 'error');
        return;
    }

    const appData = {
        company_name: company,
        job_description: jobDescription,
        resume_url,
    };
    if (state.students.length > 1) {
        appData.student_id = studentId;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/applications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify(appData),
        });

        if (response.ok) {
            showToast('Application created successfully', 'success');
            closeCreateApplicationModal();
            await loadApplicationsData();
        } else {
            let msg = 'Failed to create application';
            try {
                const err = await response.json();
                msg = formatApiDetail(err.detail) || msg;
            } catch (_) {
                /* ignore */
            }
            showToast(msg, 'error');
        }
    } catch (error) {
        console.error('Error creating application:', error);
        showToast('Error creating application', 'error');
    }
}

async function handleSettingsSave(e) {
    e.preventDefault();

    const settings = {
        name: document.getElementById('settingsName').value,
        phone: document.getElementById('settingsPhone').value,
    };

    localStorage.setItem('recruiterSettings', JSON.stringify(settings));
    showToast('Settings saved', 'success');
}

function resetSettingsForm() {
    document.getElementById('settingsForm').reset();
}

function filterStudents() {
    const search = document.getElementById('searchStudents').value.toLowerCase();

    let filtered = state.students.filter((student) => {
        const uname = (student.username || '').toLowerCase();
        return (
            student.name.toLowerCase().includes(search) ||
            student.email.toLowerCase().includes(search) ||
            uname.includes(search)
        );
    });

    displayStudents(filtered);
}

function filterApplications() {
    const search = document.getElementById('searchApplications').value.toLowerCase();
    const status = document.getElementById('appStatusFilter').value;

    let filtered = state.applications;

    if (search) {
        filtered = filtered.filter((app) => app.company_name.toLowerCase().includes(search));
    }

    if (status) {
        filtered = filtered.filter((app) => app.status === status);
    }

    displayApplicationsTable(filtered);
}

function updateAppStatus(appId) {
    const newStatus = prompt('Enter new status (applied, interview, offer, rejected):');
    if (!newStatus) return;

    showToast('Status update feature coming soon', 'info');
}

function viewStudentDetail(studentId) {
    showToast('View student feature coming soon', 'info');
}

async function createAppForStudent(studentId) {
    await openCreateApplicationModal(studentId);
}

function formatApiDetail(detail) {
    if (detail == null) return 'Request failed';
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail
            .map((item) => {
                if (typeof item === 'string') return item;
                if (item && typeof item === 'object') {
                    const loc = Array.isArray(item.loc) ? item.loc.filter((p) => p !== 'body').join('.') : '';
                    const msg = item.msg || item.message || '';
                    return loc ? `${loc}: ${msg}` : msg || JSON.stringify(item);
                }
                return String(item);
            })
            .filter(Boolean)
            .join(' · ');
    }
    if (typeof detail === 'object') {
        return detail.msg || detail.message || JSON.stringify(detail);
    }
    return String(detail);
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
