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
