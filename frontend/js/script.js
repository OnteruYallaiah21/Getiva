/* ============================================
   GETIVA - JavaScript Interactions
   ============================================ */

// Navbar background on scroll
const navbar = document.querySelector('.navbar');
const handleNavbarScroll = () => {
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(11, 11, 11, 0.95)';
        navbar.style.borderBottomColor = 'rgba(0, 229, 255, 0.2)';
    } else {
        navbar.style.background = 'rgba(11, 11, 11, 0.8)';
        navbar.style.borderBottomColor = 'rgba(42, 42, 42, 1)';
    }
};

window.addEventListener('scroll', handleNavbarScroll);

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards, role cards, and testimonial cards
document.querySelectorAll('.feature-card, .role-card, .testimonial-card, .analytics-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Button hover effects
const buttons = document.querySelectorAll('.btn');
buttons.forEach(btn => {
    btn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px)';
    });
    btn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Feature card interactive effects
const featureCards = document.querySelectorAll('.feature-card');
featureCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-12px)';
    });
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;

        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Animate stat numbers on scroll
const animateNumbers = () => {
    const statValues = document.querySelectorAll('.stat-value');

    const numberObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const target = entry.target;
                const finalValue = target.textContent;
                const isPercentage = finalValue.includes('%');
                const numericValue = parseInt(finalValue);

                target.dataset.animated = 'true';

                let currentValue = 0;
                const increment = Math.ceil(numericValue / 50);

                const counter = setInterval(() => {
                    currentValue += increment;
                    if (currentValue >= numericValue) {
                        target.textContent = finalValue;
                        clearInterval(counter);
                    } else {
                        target.textContent = isPercentage ? currentValue + '%' : currentValue;
                    }
                }, 30);

                numberObserver.unobserve(target);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(stat => numberObserver.observe(stat));
};

// Call number animation on page load
setTimeout(animateNumbers, 500);

// Table row hover effects
const tableRows = document.querySelectorAll('tbody tr');
tableRows.forEach(row => {
    row.addEventListener('mouseenter', function() {
        this.style.background = 'rgba(0, 229, 255, 0.1)';
    });
    row.addEventListener('mouseleave', function() {
        this.style.background = 'transparent';
    });
});

// Search input focus effect
const searchInput = document.querySelector('.search-input');
if (searchInput) {
    searchInput.addEventListener('focus', function() {
        this.style.borderColor = 'rgba(0, 229, 255, 0.6)';
        this.style.boxShadow = '0 0 15px rgba(0, 229, 255, 0.2)';
    });

    searchInput.addEventListener('blur', function() {
        this.style.borderColor = 'rgba(42, 42, 42, 1)';
        this.style.boxShadow = 'none';
    });
}

// Animate bars on scroll
const animateBars = () => {
    const bars = document.querySelectorAll('.bar');

    const barObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const bar = entry.target;
                const width = bar.style.width;

                bar.dataset.animated = 'true';
                bar.style.width = '0%';
                bar.style.transition = 'width 1s ease-out';

                setTimeout(() => {
                    bar.style.width = width;
                }, 100);

                barObserver.unobserve(entry.target.closest('.bar-container').querySelector('.bar'));
            }
        });
    }, { threshold: 0.5 });

    bars.forEach(bar => barObserver.observe(bar));
};

// Call bar animation on page load
setTimeout(animateBars, 700);

// Parallax effect on mouse move (subtle)
document.addEventListener('mousemove', (e) => {
    const blurs = document.querySelectorAll('.gradient-blur');

    blurs.forEach(blur => {
        const x = (e.clientX / window.innerWidth) * 20;
        const y = (e.clientY / window.innerHeight) * 20;

        blur.style.transform = `translate(${x}px, ${y}px)`;
    });
});

// Active navigation link on scroll
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

const scrollSpy = () => {
    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;

        if (scrollY >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.style.color = 'rgba(176, 176, 176, 1)';

        if (link.getAttribute('href').slice(1) === current) {
            link.style.color = 'rgba(0, 229, 255, 1)';
        }
    });
};

window.addEventListener('scroll', scrollSpy);

// Glow effect on CTA buttons
const glowButtons = document.querySelectorAll('.btn.glow');
glowButtons.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        btn.style.boxShadow = `
            0 0 20px rgba(0, 229, 255, 0.3),
            ${x - rect.width / 2}px ${y - rect.height / 2}px 40px rgba(0, 229, 255, 0.2)
        `;
    });

    btn.addEventListener('mouseleave', () => {
        btn.style.boxShadow = '0 20px 40px rgba(0, 229, 255, 0.3)';
    });
});

// Role cards click effect
const roleCards = document.querySelectorAll('.role-card');
roleCards.forEach(card => {
    card.addEventListener('click', function() {
        roleCards.forEach(c => c.style.borderColor = 'rgba(42, 42, 42, 1)');
        this.style.borderColor = 'rgba(0, 229, 255, 1)';
    });
});

// Ripple effect on button click
function createRipple(e) {
    const button = e.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    circle.style.width = circle.style.height = diameter + 'px';
    circle.style.left = e.clientX - button.offsetLeft - radius + 'px';
    circle.style.top = e.clientY - button.offsetTop - radius + 'px';
    circle.classList.add('ripple');

    const ripple = button.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }

    button.appendChild(circle);
}

buttons.forEach(button => {
    button.addEventListener('click', createRipple);
});

// Add ripple styles dynamically
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }

    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Intersection observer for section headers
const sectionHeaders = document.querySelectorAll('.section-header');
sectionHeaders.forEach(header => {
    header.style.opacity = '0';
    header.style.transform = 'translateY(40px)';
    header.style.transition = 'opacity 0.8s ease, transform 0.8s ease';

    const headerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.3 });

    headerObserver.observe(header);
});

// Dashboard container animation
const dashboardContainer = document.querySelector('.dashboard-container');
if (dashboardContainer) {
    const dbObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.2 });

    dashboardContainer.style.opacity = '0';
    dashboardContainer.style.transform = 'translateY(50px)';
    dashboardContainer.style.transition = 'opacity 0.8s ease, transform 0.8s ease';

    dbObserver.observe(dashboardContainer);
}

// Handle mobile nav toggle (if needed)
const handleMobileNav = () => {
    if (window.innerWidth <= 768) {
        // Mobile-specific behavior
        document.querySelectorAll('nav a[href^="#"]').forEach(link => {
            link.addEventListener('click', () => {
                // Close mobile menu if it exists
            });
        });
    }
};

window.addEventListener('resize', handleMobileNav);
handleMobileNav();

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search (if search existed)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput?.focus();
    }

    // Escape to blur focused element
    if (e.key === 'Escape') {
        document.activeElement.blur();
    }
});

// Page load animation
window.addEventListener('load', () => {
    document.body.style.opacity = '1';
});

// Initialize page
document.body.style.opacity = '0';
document.body.style.transition = 'opacity 0.3s ease';

// Set opacity to 1 on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        document.body.style.opacity = '1';
    });
} else {
    document.body.style.opacity = '1';
}

// Performance optimization: Lazy load images if needed
const lazyImages = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
        }
    });
});

lazyImages.forEach(img => imageObserver.observe(img));

console.log('GETIVA - Modern SaaS Platform loaded successfully');

/* ============================================
   GETIVA - Backend API Integration
   ============================================ */

// API Configuration
const API_BASE_URL = localStorage.getItem('apiBaseUrl') || 'http://localhost:8000/api';
const DASHBOARDS = {
    admin: 'admin-dashboard.html',
    recruiter: 'recruiter-dashboard.html',
    student: 'student-dashboard.html'
};

// Toast notification system
function showToast(message, type = 'success', duration = 3000) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Modal Management
function openAuthModal() {
    document.getElementById('authModal').classList.add('active');
    document.getElementById('modalOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('active');
    document.getElementById('modalOverlay').classList.remove('active');
    document.body.style.overflow = 'auto';
    resetForms();
}

function switchToRegister() {
    document.getElementById('loginForm').classList.remove('active');
    document.getElementById('registerForm').classList.add('active');
}

function switchToLogin() {
    document.getElementById('registerForm').classList.remove('active');
    document.getElementById('loginForm').classList.add('active');
}

function resetForms() {
    document.getElementById('loginFormElement').reset();
    document.getElementById('registerFormElement').reset();
    document.getElementById('loginError').textContent = '';
    document.getElementById('registerError').textContent = '';
}

// Authentication Functions
async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        
        // Store token and user info
        localStorage.setItem('authToken', data.access_token);
        localStorage.setItem('tokenType', data.token_type);
        
        // Get user role from token
        const userRole = await getUserRole(data.access_token);
        localStorage.setItem('userRole', userRole);
        
        showToast(`Welcome! Redirecting to ${userRole} dashboard...`, 'success', 2000);
        
        // Redirect after short delay
        setTimeout(() => {
            window.location.href = DASHBOARDS[userRole];
        }, 1500);
        
        return true;
    } catch (error) {
        document.getElementById('loginError').textContent = error.message;
        showToast(error.message, 'error');
        return false;
    }
}

async function register(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const data = await response.json();
        
        showToast('Account created! Logging you in...', 'success');
        
        // Auto-login after registration
        setTimeout(() => {
            switchToLogin();
            showToast('Now sign in with your credentials', 'info');
        }, 2000);
        
        return true;
    } catch (error) {
        document.getElementById('registerError').textContent = error.message;
        showToast(error.message, 'error');
        return false;
    }
}

async function getUserRole(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            return user.role;
        }
        
        // Fallback: extract role from JWT payload
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.role || 'student';
    } catch (error) {
        console.error('Error getting user role:', error);
        return 'student';
    }
}

// Check if user is already logged in
function checkExistingAuth() {
    const token = localStorage.getItem('authToken');
    if (token) {
        const role = localStorage.getItem('userRole') || 'student';
        const dashboard = DASHBOARDS[role];
        if (dashboard) {
            window.location.href = dashboard;
        }
    }
}

// Form Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Check existing auth on page load
    checkExistingAuth();

    // Sign In button
    const signInBtn = document.getElementById('signInBtn');
    if (signInBtn) {
        signInBtn.addEventListener('click', openAuthModal);
    }

    // Get Started buttons
    const startButtons = document.querySelectorAll('.btn.btn-primary.glow');
    startButtons.forEach(btn => {
        btn.addEventListener('click', openAuthModal);
    });

    // Close modal
    document.getElementById('closeAuthModal')?.addEventListener('click', closeAuthModal);
    document.getElementById('closeAuthModal2')?.addEventListener('click', closeAuthModal);
    document.getElementById('modalOverlay')?.addEventListener('click', closeAuthModal);

    // Switch between forms
    document.getElementById('switchToRegister')?.addEventListener('click', switchToRegister);
    document.getElementById('switchToLogin')?.addEventListener('click', switchToLogin);

    // Login form submission
    document.getElementById('loginFormElement')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        const submitBtn = document.getElementById('loginSubmit');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Signing in...';
        submitBtn.disabled = true;
        
        const success = await login(username, password);
        
        if (!success) {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });

    // Register form submission
    document.getElementById('registerFormElement')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            username: document.getElementById('registerUsername').value,
            email: document.getElementById('registerEmail').value,
            password: document.getElementById('registerPassword').value,
            role: document.getElementById('registerRole').value,
        };

        if (formData.role === 'student') {
            formData.full_name = document.getElementById('registerFullName').value || formData.username;
        }

        const submitBtn = document.getElementById('registerSubmit');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating account...';
        submitBtn.disabled = true;
        
        const success = await register(formData);
        
        if (!success) {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });

    // Show/hide full name field based on role
    document.getElementById('registerRole')?.addEventListener('change', (e) => {
        const fullNameGroup = document.getElementById('fullNameGroup');
        if (e.target.value === 'student') {
            fullNameGroup.style.display = 'block';
        } else {
            fullNameGroup.style.display = 'none';
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAuthModal();
        }
    });
});

// Logout function for dashboards
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('tokenType');
    localStorage.removeItem('userRole');
    window.location.href = 'index.html';
}

// API helper with authentication
async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('authToken');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('authToken');
        window.location.href = 'index.html';
        throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
    }

    return response.json();
}

