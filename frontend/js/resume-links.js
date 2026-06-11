/**
 * Resume View / Download — uses authenticated API endpoints when applicationId is set.
 */
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function getResumeApiBase() {
    return (
        (typeof localStorage !== 'undefined' && localStorage.getItem('apiBaseUrl')) ||
        `${window.location.origin}/api`
    );
}

function getResumeAuthToken() {
    return localStorage.getItem('authToken') || '';
}

async function fetchApplicationResume(applicationId, mode) {
    const token = getResumeAuthToken();
    if (!token) {
        throw new Error('Not logged in');
    }
    const path =
        mode === 'download'
            ? `/files/application/${applicationId}/resume/download`
            : `/files/application/${applicationId}/resume/view`;
    const response = await fetch(`${getResumeApiBase()}${path}`, {
        headers: { Authorization: `Bearer ${token}` },
    });
    if (response.status === 401) {
        window.location.href = 'login.html';
        throw new Error('Session expired');
    }
    if (!response.ok) {
        let msg = 'Could not load resume';
        try {
            const err = await response.json();
            if (err.detail) msg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
        } catch (_) {
            /* ignore */
        }
        throw new Error(msg);
    }
    const blob = await response.blob();
    const disposition = response.headers.get('content-disposition') || '';
    let filename = 'resume';
    const match = disposition.match(/filename="?([^";]+)"?/i);
    if (match) filename = match[1];
    return { blob, filename };
}

async function viewApplicationResume(applicationId) {
    try {
        const { blob } = await fetchApplicationResume(applicationId, 'view');
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank', 'noopener,noreferrer');
        setTimeout(() => URL.revokeObjectURL(url), 60000);
    } catch (e) {
        console.error(e);
        if (typeof showToast === 'function') showToast(e.message || 'View failed', 'error');
        else alert(e.message || 'View failed');
    }
}

async function downloadApplicationResume(applicationId) {
    try {
        const { blob, filename } = await fetchApplicationResume(applicationId, 'download');
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error(e);
        if (typeof showToast === 'function') showToast(e.message || 'Download failed', 'error');
        else alert(e.message || 'Download failed');
    }
}

function buildResumeLinksHtml(resumeUrl, applicationId) {
    if (!resumeUrl || !String(resumeUrl).trim()) {
        return '<span class="empty-inline">No resume</span>';
    }
    if (applicationId) {
        const id = escapeHtml(applicationId);
        return `
            <span class="resume-actions">
                <button type="button" class="action-btn resume-link" onclick="viewApplicationResume('${id}')">View</button>
                <button type="button" class="action-btn resume-link" onclick="downloadApplicationResume('${id}')">Download</button>
            </span>
        `;
    }
    const href = encodeURI(String(resumeUrl).trim());
    const name = href.split('/').pop().split('?')[0] || 'resume';
    return `
        <span class="resume-actions">
            <a class="action-btn resume-link" href="${href}" target="_blank" rel="noopener noreferrer">View</a>
            <a class="action-btn resume-link" href="${href}" download="${escapeHtml(name)}" rel="noopener noreferrer">Download</a>
        </span>
    `;
}
