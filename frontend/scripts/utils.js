/**
 * Utility Functions for Interactive Features
 */

// ============================================
// TOAST NOTIFICATIONS
// ============================================

class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type} fade-in`;

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.add('toast-exit');
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.remove();
                    }
                    this.toasts = this.toasts.filter(t => t !== toast);
                }, 300);
            }, duration);
        }

        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    clear() {
        this.toasts.forEach(toast => toast.remove());
        this.toasts = [];
    }
}

// Global toast instance
window.toast = new ToastManager();

// ============================================
// ANIMATED COUNTER
// ============================================

function animateCounter(element, target, duration = 2000) {
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

// ============================================
// DEBOUNCE & THROTTLE
// ============================================

function debounce(func, delay = 300) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function throttle(func, limit = 300) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// SMOOTH SCROLL
// ============================================

function smoothScroll(target, duration = 1000) {
    const targetElement = typeof target === 'string'
        ? document.querySelector(target)
        : target;

    if (!targetElement) return;

    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
}

// ============================================
// LOADING SKELETON
// ============================================

function showLoadingSkeleton(container, type = 'card', count = 3) {
    const skeletons = {
        card: `
            <div class="skeleton skeleton-card"></div>
        `,
        text: `
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text" style="width: 80%;"></div>
            <div class="skeleton skeleton-text" style="width: 60%;"></div>
        `,
        profile: `
            <div style="display: flex; align-items: center; gap: 16px;">
                <div class="skeleton skeleton-avatar"></div>
                <div style="flex: 1;">
                    <div class="skeleton skeleton-text large" style="width: 200px;"></div>
                    <div class="skeleton skeleton-text" style="width: 150px;"></div>
                </div>
            </div>
        `,
        job: `
            <div class="card" style="padding: 20px;">
                <div class="skeleton skeleton-text large" style="width: 70%; margin-bottom: 12px;"></div>
                <div class="skeleton skeleton-text" style="width: 50%; margin-bottom: 16px;"></div>
                <div class="skeleton skeleton-text" style="width: 100%;"></div>
                <div class="skeleton skeleton-text" style="width: 90%;"></div>
                <div style="display: flex; gap: 8px; margin-top: 16px;">
                    <div class="skeleton skeleton-button"></div>
                    <div class="skeleton skeleton-button"></div>
                </div>
            </div>
        `
    };

    const skeleton = skeletons[type] || skeletons.card;
    container.innerHTML = skeleton.repeat(count);
}

function hideLoadingSkeleton(container) {
    container.innerHTML = '';
}

// ============================================
// SCROLL REVEAL ANIMATION
// ============================================

function initScrollReveal() {
    const reveals = document.querySelectorAll('.scroll-reveal');

    const revealOnScroll = () => {
        reveals.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;

            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('revealed');
            }
        });
    };

    window.addEventListener('scroll', throttle(revealOnScroll, 100));
    revealOnScroll(); // Initial check
}

// ============================================
// CIRCULAR PROGRESS
// ============================================

function setCircularProgress(element, percentage) {
    const circle = element.querySelector('.circular-progress-fill');
    const text = element.querySelector('.circular-progress-text');

    if (!circle) return;

    const radius = circle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    circle.style.strokeDasharray = `${circumference} ${circumference}`;
    circle.style.strokeDashoffset = offset;

    if (text) {
        text.textContent = `${Math.round(percentage)}%`;
    }
}

// ============================================
// PROGRESS BAR
// ============================================

function setProgress(element, percentage, animated = true) {
    const fill = element.querySelector('.progress-fill');
    if (!fill) return;

    if (animated) {
        setTimeout(() => {
            fill.style.width = `${percentage}%`;
        }, 100);
    } else {
        fill.style.width = `${percentage}%`;
    }
}

// ============================================
// MODAL HELPERS
// ============================================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.style.display = 'flex';
    modal.classList.add('fade-in');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.add('fade-out');
    setTimeout(() => {
        modal.style.display = 'none';
        modal.classList.remove('fade-out');
        document.body.style.overflow = '';
    }, 300);
}

// ============================================
// FORMAT HELPERS
// ============================================

function formatDate(date) {
    const d = new Date(date);
    const now = new Date();
    const diff = now - d;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return `${Math.floor(days / 365)} years ago`;
}

function formatSalary(min, max, currency = '$') {
    if (!min && !max) return 'Not specified';
    if (!max) return `${currency}${(min / 1000).toFixed(0)}k+`;
    return `${currency}${(min / 1000).toFixed(0)}k - ${currency}${(max / 1000).toFixed(0)}k`;
}

function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// ============================================
// COPY TO CLIPBOARD
// ============================================

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        toast.success('Copied to clipboard!');
        return true;
    } catch (err) {
        toast.error('Failed to copy to clipboard');
        return false;
    }
}

// ============================================
// INITIALIZE ON LOAD
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize scroll reveal
    initScrollReveal();

    // Add smooth scroll to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                smoothScroll(target);
            }
        });
    });

    // Animate counters on page load
    document.querySelectorAll('[data-counter]').forEach(element => {
        const target = parseInt(element.getAttribute('data-counter'));
        animateCounter(element, target);
    });
});

// Export utilities
window.utils = {
    animateCounter,
    debounce,
    throttle,
    smoothScroll,
    showLoadingSkeleton,
    hideLoadingSkeleton,
    setCircularProgress,
    setProgress,
    openModal,
    closeModal,
    formatDate,
    formatSalary,
    truncateText,
    copyToClipboard
};
