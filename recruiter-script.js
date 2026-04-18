/* ============================================
   GETIVA Recruiter Dashboard JavaScript
   ============================================ */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';
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
        state.currentUser = {
            id: 'recruiter-id',
            name: 'Recruiter Name',
            email: 'recruiter@example.com',
        };
        document.getElementById('recruiterName').textContent = state.currentUser.name;
        document.getElementById('recruiterGreeting').textContent = state.currentUser.name.split(' ')[0];
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
    document.getElementById('addStudentForm')?.addEventListener('submit', handleAddStudent);
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

async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/applications`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const stats = await response.json();

        // Update stat cards
        const total = stats.total_applications || 1;
        document.getElementById('totalStudents').textContent = '0'; // TODO: Get from API
        document.getElementById('totalApplications').textContent = stats.total_applications;
        document.getElementById('interviewCount').textContent = stats.interview_count;
        document.getElementById('offerCount').textContent = stats.offer_count;

        // Update success rate
        const successRate = Math.round((stats.offer_count / total) * 100);
        document.getElementById('successRate').textContent = successRate;
        updateSuccessCircle(successRate);

        // Update month stats (simulated)
        document.getElementById('monthApps').textContent = Math.floor(stats.total_applications * 0.3);
        document.getElementById('monthInterviews').textContent = Math.floor(stats.interview_count * 0.4);
        document.getElementById('monthOffers').textContent = Math.floor(stats.offer_count * 0.5);

        // Load recent applications
        await loadRecentApplications();
        await loadStudentsData();
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showToast('Failed to load dashboard', 'error');
    }
}

async function loadRecentApplications() {
    try {
        const response = await fetch(`${API_BASE_URL}/applications?page=1&per_page=5`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        const container = document.getElementById('recentApps');
        container.innerHTML = '';

        data.items?.slice(0, 5).forEach((app) => {
            const div = document.createElement('div');
            div.className = 'recent-app-item';
            div.innerHTML = `
                <strong>${app.company_name}</strong>
                <span>${app.job_title} • ${new Date(app.applied_date).toLocaleDateString()}</span>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Failed to load recent applications:', error);
    }
}

async function loadStudentsData() {
    try {
        // Mock data for students
        state.students = [
            {
                id: '1',
                name: 'John Doe',
                email: 'john@example.com',
                phone: '555-0100',
                applications: 12,
                interviews: 3,
                offers: 1,
            },
            {
                id: '2',
                name: 'Jane Smith',
                email: 'jane@example.com',
                phone: '555-0101',
                applications: 8,
                interviews: 2,
                offers: 1,
            },
        ];

        if (state.currentSection === 'dashboard') {
            document.getElementById('totalStudents').textContent = state.students.length;
        } else {
            displayStudents(state.students);
        }
    } catch (error) {
        console.error('Failed to load students:', error);
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
                <div class="student-email">${student.email}</div>
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

function displayApplicationsTable(applications) {
    const tbody = document.getElementById('applicationsTable');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (applications.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty">No applications</td></tr>';
        return;
    }

    applications.forEach((app) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${app.student_id.substring(0, 8)}</td>
            <td>${app.company_name}</td>
            <td>${app.job_title}</td>
            <td><span class="status-badge status-${app.status}">${app.status}</span></td>
            <td>${new Date(app.applied_date).toLocaleDateString()}</td>
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
        const stats = await response.json();

        // Update breakdown stats
        const total = stats.total_applications || 1;
        document.getElementById('appliedCount').textContent = stats.applied_count;
        document.getElementById('appliedProgress').style.width = `${(stats.applied_count / total) * 100}%`;

        document.getElementById('interviewCount2').textContent = stats.interview_count;
        document.getElementById('interviewProgress').style.width = `${(stats.interview_count / total) * 100}%`;

        document.getElementById('offerCount2').textContent = stats.offer_count;
        document.getElementById('offerProgress').style.width = `${(stats.offer_count / total) * 100}%`;

        // Update funnel
        document.getElementById('funnelApplied').textContent = stats.applied_count;
        document.getElementById('funnelInterview').textContent = stats.interview_count;
        document.getElementById('funnelOffer').textContent = stats.offer_count;

        // Load student performance table
        displayStudentPerformance(state.students);
    } catch (error) {
        console.error('Failed to load performance:', error);
    }
}

function displayStudentPerformance(students) {
    const tbody = document.getElementById('studentPerformanceTable');
    if (!tbody) return;

    tbody.innerHTML = '';

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
        // Mock payment data
        const mockPayments = [
            { month: '2024-01', amount: 2000, status: 'completed', date: '2024-02-01' },
            { month: '2023-12', amount: 2000, status: 'completed', date: '2024-01-01' },
            { month: '2023-11', amount: 1500, status: 'completed', date: '2023-12-01' },
        ];

        state.payments = mockPayments;

        const totalEarned = mockPayments.reduce((sum, p) => sum + parseFloat(p.amount), 0);
        const totalPaid = mockPayments.filter(p => p.status === 'completed').reduce((sum, p) => sum + parseFloat(p.amount), 0);
        const totalPending = mockPayments.filter(p => p.status === 'pending').reduce((sum, p) => sum + parseFloat(p.amount), 0);

        document.getElementById('totalEarned').textContent = `$${totalEarned.toFixed(2)}`;
        document.getElementById('totalPaid').textContent = `$${totalPaid.toFixed(2)}`;
        document.getElementById('totalPending').textContent = `$${totalPending.toFixed(2)}`;

        displayPaymentsTable(mockPayments);
    } catch (error) {
        console.error('Failed to load payments:', error);
    }
}

function displayPaymentsTable(payments) {
    const tbody = document.getElementById('paymentsTable');
    if (!tbody) return;

    tbody.innerHTML = '';

    payments.forEach((payment) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${payment.month}</td>
            <td>$${parseFloat(payment.amount).toFixed(2)}</td>
            <td><span class="status-badge status-${payment.status}">${payment.status}</span></td>
            <td>${new Date(payment.date).toLocaleDateString()}</td>
        `;
        tbody.appendChild(row);
    });
}

async function loadSettingsData() {
    document.getElementById('settingsName').value = state.currentUser?.name || '';
    document.getElementById('settingsEmail').value = state.currentUser?.email || '';
}

// ============================================
// USER INTERACTIONS
// ============================================

function openCreateApplicationModal() {
    const select = document.getElementById('studentSelect');
    select.innerHTML = '<option value="">-- Choose Student --</option>';

    state.students.forEach((student) => {
        const option = document.createElement('option');
        option.value = student.id;
        option.textContent = student.name;
        select.appendChild(option);
    });

    document.getElementById('createApplicationModal').classList.add('active');
}

function closeCreateApplicationModal() {
    document.getElementById('createApplicationModal').classList.remove('active');
    document.getElementById('applicationForm').reset();
}

function openAddStudentModal() {
    document.getElementById('addStudentModal').classList.add('active');
}

function closeAddStudentModal() {
    document.getElementById('addStudentModal').classList.remove('active');
    document.getElementById('addStudentForm').reset();
}

async function handleCreateApplication(e) {
    e.preventDefault();

    const appData = {
        student_id: document.getElementById('studentSelect').value,
        company_name: document.getElementById('companyName').value,
        job_title: document.getElementById('jobTitle').value,
        job_description: document.getElementById('jobDescription').value,
        job_url: document.getElementById('jobUrl').value,
    };

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
            showToast('Failed to create application', 'error');
        }
    } catch (error) {
        console.error('Error creating application:', error);
        showToast('Error creating application', 'error');
    }
}

async function handleAddStudent(e) {
    e.preventDefault();

    const studentData = {
        username: document.getElementById('studentEmail').value.split('@')[0],
        email: document.getElementById('studentEmail').value,
        password: 'TempPassword123!',
        role: 'student',
        full_name: document.getElementById('studentFullName').value,
    };

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify(studentData),
        });

        if (response.ok) {
            showToast('Student added successfully', 'success');
            closeAddStudentModal();
            await loadStudentsData();
        } else {
            showToast('Failed to add student', 'error');
        }
    } catch (error) {
        console.error('Error adding student:', error);
        showToast('Error adding student', 'error');
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

    let filtered = state.students.filter((student) =>
        student.name.toLowerCase().includes(search) || student.email.toLowerCase().includes(search)
    );

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

function createAppForStudent(studentId) {
    openCreateApplicationModal();
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
