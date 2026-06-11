/* ============================================
   GETIVA Admin Dashboard JavaScript
   ============================================ */

// Configuration
const API_BASE_URL =
    (typeof localStorage !== 'undefined' && localStorage.getItem('apiBaseUrl')) ||
    `${window.location.origin}/api`;
let authToken = localStorage.getItem('authToken');

// State management
const state = {
    currentUser: null,
    currentPage: 'dashboard',
    users: [],
    applications: [],
    payments: [],
    analytics: null,
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

        if (u.role !== 'admin') {
            localStorage.setItem('userRole', u.role);
            if (u.role === 'student') {
                window.location.href = 'student-dashboard.html';
            } else if (u.role === 'recruiter') {
                window.location.href = 'recruiter-dashboard.html';
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
        document.getElementById('userName').textContent = u.username;
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

    document.querySelectorAll('[data-section-jump]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            switchSection(btn.getAttribute('data-section-jump'));
        });
    });

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // User modal
    document.getElementById('addUserBtn')?.addEventListener('click', openUserModal);
    document.querySelector('.close-btn')?.addEventListener('click', closeUserModal);
    document.getElementById('userForm')?.addEventListener('submit', handleAddUser);

    document.getElementById('resetPasswordForm')?.addEventListener('submit', handleResetPasswordSubmit);
    document.getElementById('closeResetPwModal')?.addEventListener('click', closeResetPasswordModal);
    document.getElementById('cancelResetPw')?.addEventListener('click', closeResetPasswordModal);

    document.getElementById('closeCredentialShareModal')?.addEventListener('click', closeCredentialShareModal);
    document.getElementById('dismissCredentialShare')?.addEventListener('click', closeCredentialShareModal);
    document.getElementById('copyCredentialsBtn')?.addEventListener('click', copySharedCredentials);

    document.getElementById('uploadDocBtn')?.addEventListener('click', handleAdminDocumentUpload);
    document.getElementById('reloadLandingPreview')?.addEventListener('click', reloadLandingPreview);

    // Payment tabs
    document.querySelectorAll('.tab-btn').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            switchTab(tab);
        });
    });

    // Filters
    document.getElementById('roleFilter')?.addEventListener('change', filterUsers);
    document.getElementById('statusFilter')?.addEventListener('change', filterUsers);
    document.getElementById('appStatusFilter')?.addEventListener('change', filterApplications);
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
        dashboard: 'Dashboard',
        users: 'User Management',
        documents: 'Document storage',
        applications: 'Applications',
        payments: 'Payments',
        analytics: 'Analytics',
        reports: 'Reports',
        landing: 'Landing Page',
    };
    document.getElementById('pageTitle').textContent = titles[sectionName] || 'Dashboard';

    state.currentPage = sectionName;

    // Load section data
    loadSectionData(sectionName);
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach((tab) => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach((btn) => btn.classList.remove('active'));

    // Show selected tab
    const tab = document.getElementById(tabName);
    if (tab) {
        tab.classList.add('active');
    }

    // Update tab button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Load tab data
    if (tabName.includes('student')) {
        loadStudentPayments();
    } else {
        loadRecruiterPayments();
    }
}

// ============================================
// DATA LOADING
// ============================================

async function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'dashboard':
            await loadDashboardData();
            break;
        case 'users':
            await loadUsers();
            break;
        case 'documents':
            await loadAdminDocuments();
            break;
        case 'applications':
            await loadApplications();
            break;
        case 'payments':
            await loadStudentPayments();
            break;
        case 'analytics':
            await loadAnalytics();
            break;
        case 'reports':
            // Reports data is generated on demand
            break;
        case 'landing':
            reloadLandingPreview();
            break;
    }
}

function reloadLandingPreview() {
    const frame = document.getElementById('landingOldFrame');
    if (!frame) return;
    frame.src = '/index-old.html';
}

async function loadDashboardData() {
    try {
        // Load analytics data
        const response = await fetch(`${API_BASE_URL}/analytics/system`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        state.analytics = data;

        // Update stat cards
        document.getElementById('totalStudents').textContent = data.total_students;
        document.getElementById('totalRecruiters').textContent = data.total_recruiters;
        document.getElementById('totalApplications').textContent = data.total_applications;
        document.getElementById('totalRevenue').textContent = `$${data.total_revenue.toFixed(2)}`;

        // Update financial stats
        document.getElementById('dashRevenue').textContent = `$${data.financial_report.total_revenue.toFixed(2)}`;
        document.getElementById('dashPaidOut').textContent = `$${data.financial_report.total_paid.toFixed(2)}`;
        document.getElementById('dashProfit').textContent = `$${data.financial_report.net_profit.toFixed(2)}`;

        // Update status breakdown
        const stats = data.application_stats;
        const total = stats.total_applications || 1;

        document.getElementById('appliedCount').textContent = stats.applied_count;
        document.getElementById('appliedProgress').style.width = `${(stats.applied_count / total) * 100}%`;

        document.getElementById('interviewCount').textContent = stats.interview_count;
        document.getElementById('interviewProgress').style.width = `${(stats.interview_count / total) * 100}%`;

        document.getElementById('offerCount').textContent = stats.offer_count;
        document.getElementById('offerProgress').style.width = `${(stats.offer_count / total) * 100}%`;

        // Load recent applications
        await loadRecentApplications();
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

async function loadRecentApplications() {
    try {
        const response = await fetch(`${API_BASE_URL}/applications?page=1&per_page=5`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        const tbody = document.getElementById('recentApplications');
        tbody.innerHTML = '';

        if (data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty">No recent applications</td></tr>';
            return;
        }

        data.items.forEach((app) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${app.student_id.substring(0, 8)}...</td>
                <td>${app.company_name}</td>
                <td>${app.job_title}</td>
                <td><span class="status-badge status-${app.status}">${app.status}</span></td>
                <td>${formatDateTime(app.applied_date)}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load recent applications:', error);
    }
}

async function loadAdminDocuments() {
    const tbody = document.getElementById('documentsTable');
    if (!tbody) return;
    try {
        const response = await fetch(`${API_BASE_URL}/files/admin/documents`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        if (!response.ok) {
            throw new Error('Failed to fetch documents');
        }
        const items = await response.json();
        tbody.innerHTML = '';
        if (!items.length) {
            tbody.innerHTML =
                '<tr><td colspan="4" class="empty">No documents yet. Upload a file — it goes to Supabase; the URL is stored in Neon.</td></tr>';
            return;
        }
        items.forEach((doc) => {
            const row = document.createElement('tr');
            const link = doc.storage_url.replace(/"/g, '&quot;');
            row.innerHTML = `
                <td>${doc.title || '—'}</td>
                <td>${doc.file_name}</td>
                <td><a href="${link}" target="_blank" rel="noopener noreferrer">Open</a></td>
                <td>${new Date(doc.created_at).toLocaleString()}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load documents:', error);
        tbody.innerHTML =
            '<tr><td colspan="4" class="empty">Failed to load documents. Check Supabase env and migration.</td></tr>';
    }
}

async function handleAdminDocumentUpload() {
    const titleEl = document.getElementById('docTitle');
    const fileInput = document.getElementById('docFile');
    if (!fileInput?.files?.length) {
        showToast('Choose a file first', 'error');
        return;
    }
    const fd = new FormData();
    fd.append('file', fileInput.files[0]);
    const t = (titleEl?.value || '').trim();
    if (t) {
        fd.append('title', t);
    }
    const btn = document.getElementById('uploadDocBtn');
    btn.disabled = true;
    try {
        const response = await fetch(`${API_BASE_URL}/files/admin/documents`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${authToken}` },
            body: fd,
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            showToast(typeof err.detail === 'string' ? err.detail : 'Upload failed', 'error');
            return;
        }
        showToast('File stored in Supabase; URL saved in Neon', 'success');
        if (titleEl) titleEl.value = '';
        fileInput.value = '';
        await loadAdminDocuments();
    } catch (error) {
        console.error(error);
        showToast('Upload failed', 'error');
    } finally {
        btn.disabled = false;
    }
}

async function loadUsers(page = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/users?page=${page}&per_page=10`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }

        const data = await response.json();
        state.users = data.items;

        displayUsers(data.items);
        displayPagination(data, 'pagination', () => loadUsers(page));
    } catch (error) {
        console.error('Failed to load users:', error);
        document.getElementById('usersTable').innerHTML =
            '<tr><td colspan="6" class="empty">Failed to load users</td></tr>';
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('usersTable');
    tbody.innerHTML = '';

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty">No users found</td></tr>';
        return;
    }

    users.forEach((user) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td><span class="label-role label-role-${user.role}">${user.role}</span></td>
            <td>${user.is_active ? '<span class="status-badge status-completed">Active</span>' : '<span class="status-badge status-rejected">Inactive</span>'}</td>
            <td>${formatDateTime(user.created_at)}</td>
            <td>
                <button class="action-btn" onclick="editUser('${user.id}')">Edit</button>
                <button class="action-btn" onclick="window.openResetPasswordModal('${user.id}')">Reset password</button>
                <button class="action-btn" onclick="toggleUserStatus('${user.id}')">Toggle</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function loadApplications(page = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/applications?page=${page}&per_page=10`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        const tbody = document.getElementById('applicationsTable');
        tbody.innerHTML = '';

        if (data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty">No applications found</td></tr>';
            return;
        }

        data.items.forEach((app) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${app.student_id.substring(0, 8)}...</td>
                <td>${app.company_name}</td>
                <td>${app.job_title}</td>
                <td>${app.recruiter_id.substring(0, 8)}...</td>
                <td><span class="status-badge status-${app.status}">${app.status}</span></td>
                <td>${formatDateTime(app.applied_date)}</td>
                <td>${buildResumeLinksHtml(app.resume_url, app.id)}</td>
                <td>
                    <button class="action-btn" onclick="updateApplicationStatus('${app.id}')">Update</button>
                </td>
            `;
            tbody.appendChild(row);
        });

        displayPagination(data, 'appPagination', () => loadApplications(page));
    } catch (error) {
        console.error('Failed to load applications:', error);
        document.getElementById('applicationsTable').innerHTML =
            '<tr><td colspan="8" class="empty">Failed to load applications</td></tr>';
    }
}

async function loadStudentPayments() {
    try {
        const response = await fetch(`${API_BASE_URL}/payments/student?page=1&per_page=10`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        const tbody = document.getElementById('studentPaymentsTable');
        tbody.innerHTML = '';

        if (data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty">No payment records</td></tr>';
            return;
        }

        data.items.forEach((payment) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${payment.student_id.substring(0, 8)}...</td>
                <td>$${payment.amount}</td>
                <td>${payment.payment_type}</td>
                <td><span class="status-badge status-${payment.status}">${payment.status}</span></td>
                <td>${formatDateTime(payment.payment_date)}</td>
                <td>
                    <button class="action-btn" onclick="updatePaymentStatus('${payment.id}', 'student')">Update</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load student payments:', error);
    }
}

async function loadRecruiterPayments() {
    try {
        const response = await fetch(`${API_BASE_URL}/payments/recruiter?page=1&per_page=10`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        const tbody = document.getElementById('recruiterPaymentsTable');
        tbody.innerHTML = '';

        if (data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty">No payment records</td></tr>';
            return;
        }

        data.items.forEach((payment) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${payment.recruiter_id.substring(0, 8)}...</td>
                <td>$${payment.amount}</td>
                <td>${payment.salary_month}</td>
                <td><span class="status-badge status-${payment.status}">${payment.status}</span></td>
                <td>${formatDateTime(payment.payment_date)}</td>
                <td>
                    <button class="action-btn" onclick="updatePaymentStatus('${payment.id}', 'recruiter')">Update</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load recruiter payments:', error);
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/system`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const data = await response.json();

        // Load recruiter performance
        const perfResponse = await fetch(`${API_BASE_URL}/analytics/recruiters`, {
            headers: { Authorization: `Bearer ${authToken}` },
        });
        const perfData = await perfResponse.json();

        displayRecruiterPerformance(perfData.recruiters);
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

function displayRecruiterPerformance(recruiters) {
    const container = document.querySelector('.recruiter-list');
    container.innerHTML = '';

    recruiters.slice(0, 5).forEach((recruiter) => {
        const div = document.createElement('div');
        div.className = 'recruiter-item';
        div.innerHTML = `
            <div class="recruiter-info">
                <div class="recruiter-name">${recruiter.recruiter_name}</div>
                <div class="recruiter-apps">${recruiter.total_applications} applications</div>
            </div>
            <div class="recruiter-rate">${recruiter.success_rate}%</div>
        `;
        container.appendChild(div);
    });
}

// ============================================
// USER MANAGEMENT
// ============================================

function openUserModal() {
    document.getElementById('userModal').classList.add('active');
}

function closeUserModal() {
    document.getElementById('userModal').classList.remove('active');
    document.getElementById('userForm').reset();
}

async function handleAddUser(e) {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const plainPassword = document.getElementById('password').value;
    const role = document.getElementById('role').value;

    if (username.length < 3) {
        showToast('Username must be at least 3 characters', 'error');
        return;
    }
    if (plainPassword.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }
    if (!role) {
        showToast('Choose a role (student, recruiter, or admin)', 'error');
        return;
    }

    const userData = {
        username,
        password: plainPassword,
        role,
    };
    const email = document.getElementById('email').value.trim();
    if (email) {
        userData.email = email;
    }
    const fullName = document.getElementById('fullName').value.trim();
    if (fullName) {
        userData.full_name = fullName;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify(userData),
        });

        if (response.ok) {
            const createdUsername = userData.username;
            closeUserModal();
            showToast('User created', 'success');
            showCredentialShareModal(createdUsername, plainPassword);
            await loadUsers();
        } else {
            let msg = 'Failed to create user';
            try {
                const error = await response.json();
                msg = formatApiDetail(error.detail) || msg;
            } catch {
                msg = `Failed (${response.status})`;
            }
            showToast(msg, 'error');
        }
    } catch (error) {
        console.error('Error creating user:', error);
        showToast('Failed to create user', 'error');
    }
}

function showCredentialShareModal(username, password) {
    document.getElementById('shareCredUsername').value = username;
    document.getElementById('shareCredPassword').value = password;
    document.getElementById('credentialShareModal').classList.add('active');
}

function closeCredentialShareModal() {
    document.getElementById('shareCredPassword').value = '';
    document.getElementById('credentialShareModal').classList.remove('active');
}

async function copySharedCredentials() {
    const u = document.getElementById('shareCredUsername').value;
    const p = document.getElementById('shareCredPassword').value;
    const text = `Username: ${u}\nPassword: ${p}`;
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard', 'success');
    } catch {
        showToast('Copy failed — select and copy manually', 'error');
    }
}

window.openResetPasswordModal = function openResetPasswordModal(userId) {
    const u = state.users.find((x) => x.id === userId);
    document.getElementById('resetPwUserId').value = userId;
    document.getElementById('resetPwUsername').textContent = u ? u.username : userId;
    document.getElementById('resetPwNew').value = '';
    document.getElementById('resetPwConfirm').value = '';
    document.getElementById('resetPasswordModal').classList.add('active');
};

function closeResetPasswordModal() {
    document.getElementById('resetPasswordModal').classList.remove('active');
}

async function handleResetPasswordSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('resetPwUserId').value;
    const profile = state.users.find((x) => x.id === id);
    const uname = profile ? profile.username : id;
    const p1 = document.getElementById('resetPwNew').value;
    const p2 = document.getElementById('resetPwConfirm').value;
    if (p1 !== p2) {
        showToast('Passwords do not match', 'error');
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/auth/users/${id}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify({ new_password: p1 }),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            showToast(typeof err.detail === 'string' ? err.detail : 'Reset failed', 'error');
            return;
        }
        closeResetPasswordModal();
        showCredentialShareModal(uname, p1);
        await loadUsers();
    } catch (err) {
        console.error(err);
        showToast('Reset failed', 'error');
    }
}

async function toggleUserStatus(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/users/${userId}/toggle-status`, {
            method: 'PATCH',
            headers: { Authorization: `Bearer ${authToken}` },
        });

        if (response.ok) {
            showToast('User status updated', 'success');
            await loadUsers();
        }
    } catch (error) {
        console.error('Error updating user:', error);
        showToast('Failed to update user', 'error');
    }
}

// ============================================
// FILTERING
// ============================================

function filterUsers() {
    const roleFilter = document.getElementById('roleFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;

    let filtered = state.users;

    if (roleFilter) {
        filtered = filtered.filter((user) => user.role === roleFilter);
    }

    if (statusFilter !== '') {
        filtered = filtered.filter((user) => user.is_active.toString() === statusFilter);
    }

    displayUsers(filtered);
}

function filterApplications() {
    const statusFilter = document.getElementById('appStatusFilter').value;

    let filtered = state.applications;

    if (statusFilter) {
        filtered = filtered.filter((app) => app.status === statusFilter);
    }

    displayApplications(filtered);
}

// ============================================
// PAYMENT MANAGEMENT
// ============================================

async function updatePaymentStatus(paymentId, type) {
    const newStatus = prompt('Enter new status (pending, completed, failed, refunded):');

    if (!newStatus) return;

    try {
        const endpoint = type === 'student' ? 'student' : 'recruiter';
        const response = await fetch(`${API_BASE_URL}/payments/${endpoint}/${paymentId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify({ status: newStatus }),
        });

        if (response.ok) {
            showToast('Payment status updated', 'success');
            type === 'student' ? await loadStudentPayments() : await loadRecruiterPayments();
        }
    } catch (error) {
        console.error('Error updating payment:', error);
        showToast('Failed to update payment', 'error');
    }
}

// ============================================
// REPORTING
// ============================================

async function generateReport(reportType) {
    const output = document.getElementById('reportOutput');
    const content = document.getElementById('reportContent');

    try {
        let data;
        const title = {
            applications: 'Application Report',
            financial: 'Financial Report',
            recruiter: 'Recruiter Performance Report',
            student: 'Student Progress Report',
        };

        document.getElementById('reportTitle').textContent = title[reportType];

        if (reportType === 'applications') {
            const response = await fetch(`${API_BASE_URL}/applications`, {
                headers: { Authorization: `Bearer ${authToken}` },
            });
            data = await response.json();
            content.innerHTML = generateApplicationReport(data.items);
        } else if (reportType === 'financial') {
            const response = await fetch(`${API_BASE_URL}/analytics/financial`, {
                headers: { Authorization: `Bearer ${authToken}` },
            });
            data = await response.json();
            content.innerHTML = generateFinancialReport(data);
        } else if (reportType === 'recruiter') {
            const response = await fetch(`${API_BASE_URL}/analytics/recruiters`, {
                headers: { Authorization: `Bearer ${authToken}` },
            });
            data = await response.json();
            content.innerHTML = generateRecruiterReport(data.recruiters);
        }

        output.style.display = 'block';
    } catch (error) {
        console.error('Error generating report:', error);
        showToast('Failed to generate report', 'error');
    }
}

function generateApplicationReport(applications) {
    let html = '<h3>Application Summary</h3>';
    html += `<p>Total Applications: ${applications.length}</p>`;

    const byStatus = {};
    applications.forEach((app) => {
        byStatus[app.status] = (byStatus[app.status] || 0) + 1;
    });

    html += '<h4>By Status:</h4><ul>';
    Object.entries(byStatus).forEach(([status, count]) => {
        html += `<li>${status}: ${count}</li>`;
    });
    html += '</ul>';

    return html;
}

function generateFinancialReport(data) {
    return `
        <h3>Financial Summary</h3>
        <ul>
            <li><strong>Total Revenue:</strong> $${data.total_revenue}</li>
            <li><strong>Total Paid Out:</strong> $${data.total_paid}</li>
            <li><strong>Net Profit:</strong> $${data.net_profit}</li>
            <li><strong>Student Payments:</strong> ${data.student_payments_count}</li>
            <li><strong>Recruiter Payments:</strong> ${data.recruiter_payments_count}</li>
        </ul>
    `;
}

function generateRecruiterReport(recruiters) {
    let html = '<h3>Recruiter Performance</h3><table class="data-table"><thead><tr><th>Recruiter</th><th>Apps</th><th>Success Rate</th></tr></thead><tbody>';

    recruiters.forEach((recruiter) => {
        html += `<tr><td>${recruiter.recruiter_name}</td><td>${recruiter.total_applications}</td><td>${recruiter.success_rate}%</td></tr>`;
    });

    html += '</tbody></table>';
    return html;
}

function printReport() {
    window.print();
}

function downloadReport() {
    const reportContent = document.getElementById('reportContent').innerHTML;
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/html;charset=utf-8,' + encodeURIComponent(reportContent));
    element.setAttribute('download', 'report.html');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// ============================================
// UTILITIES
// ============================================

function displayPagination(data, elementId, loadMoreCallback) {
    const container = document.getElementById(elementId);
    if (!container) return;

    container.innerHTML = '';

    for (let i = 1; i <= Math.ceil(data.total / data.per_page); i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.className = i === data.page ? 'active' : '';
        button.addEventListener('click', () => loadMoreCallback(i));
        container.appendChild(button);
    }
}

/** Turn FastAPI / Pydantic error bodies into a readable string (avoids "[object Object]"). */
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
document.getElementById('userModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'userModal') {
        closeUserModal();
    }
});
