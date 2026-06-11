/**
 * GETIVA — login & change-password (admin-provisioned accounts only).
 */
(function () {
    const API_BASE =
        localStorage.getItem('apiBaseUrl') || `${window.location.origin}/api`;
    const DASHBOARDS = {
        admin: 'admin-dashboard.html',
        recruiter: 'recruiter-dashboard.html',
        student: 'student-dashboard.html',
    };

    async function fetchRole(token) {
        const r = await fetch(`${API_BASE}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!r.ok) {
            throw new Error('Could not load profile');
        }
        const u = await r.json();
        return u.role;
    }

    const loginForm = document.getElementById('loginFormElement');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errEl = document.getElementById('loginError');
            errEl.textContent = '';
            const btn = document.getElementById('loginSubmit');
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const prevLabel = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Signing in…';
            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });
                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    errEl.textContent =
                        typeof data.detail === 'string' ? data.detail : 'Sign in failed';
                    return;
                }
                localStorage.setItem('authToken', data.access_token);
                localStorage.setItem('tokenType', data.token_type || 'bearer');
                localStorage.setItem(
                    'mustChangePassword',
                    data.must_change_password ? 'true' : 'false',
                );
                const role = await fetchRole(data.access_token);
                localStorage.setItem('userRole', role);
                if (data.must_change_password) {
                    window.location.href = 'change-password.html';
                } else {
                    window.location.href = DASHBOARDS[role] || 'index.html';
                }
            } catch (ex) {
                errEl.textContent = ex.message || 'Sign in failed';
            } finally {
                btn.disabled = false;
                btn.textContent = prevLabel;
            }
        });
    }

    const cpForm = document.getElementById('changePasswordFormElement');
    if (cpForm) {
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }
        if (localStorage.getItem('mustChangePassword') !== 'true') {
            const role = localStorage.getItem('userRole');
            if (role && DASHBOARDS[role]) {
                window.location.href = DASHBOARDS[role];
            }
        }

        cpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errEl = document.getElementById('changePasswordError');
            errEl.textContent = '';
            const current = document.getElementById('currentPassword').value;
            const next = document.getElementById('newPassword').value;
            const confirm = document.getElementById('confirmPassword').value;
            if (next !== confirm) {
                errEl.textContent = 'New passwords do not match';
                return;
            }
            const btn = document.getElementById('changePasswordSubmit');
            const prevLabel = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Saving…';
            try {
                const res = await fetch(`${API_BASE}/auth/change-password`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${localStorage.getItem('authToken')}`,
                    },
                    body: JSON.stringify({
                        current_password: current,
                        new_password: next,
                    }),
                });
                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    errEl.textContent =
                        typeof data.detail === 'string' ? data.detail : 'Could not update password';
                    return;
                }
                localStorage.setItem('authToken', data.access_token);
                localStorage.setItem('mustChangePassword', 'false');
                const role = localStorage.getItem('userRole') || (await fetchRole(data.access_token));
                window.location.href = DASHBOARDS[role] || 'index.html';
            } catch (ex) {
                errEl.textContent = ex.message || 'Could not update password';
            } finally {
                btn.disabled = false;
                btn.textContent = prevLabel;
            }
        });
    }

    document.querySelectorAll('[data-auth-toggle]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-auth-toggle');
            const input = id ? document.getElementById(id) : null;
            if (!input || (input.type !== 'password' && input.type !== 'text')) {
                return;
            }
            const show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            btn.textContent = show ? 'Hide' : 'Show';
            btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
        });
    });
})();
