/**
 * Recruiter Dashboard JavaScript - Handle all recruiter dashboard interactions
 */

const api = new APIClient();
let dashboardData = {
    user: null,
    activeJobs: [],
    recentApplicants: []
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!requireAuth()) return;

    // Load all dashboard data
    await loadDashboard();

    // Setup event listeners
    setupEventListeners();

    // Setup auto-refresh (every 30 seconds)
    setInterval(refreshDashboard, 30000);
});

// ============================================
// LOAD DASHBOARD DATA
// ============================================

async function loadDashboard() {
    try {
        // Show loading skeletons
        showLoadingStates();

        const user = await api.getProfile().catch(() => null);

        // For now, we'll try to fetch jobs. In a real app, this would be "my posted jobs"
        // We'll pass a dummy filter or assume the backend filters if we use a specific endpoint
        // Since we don't have getMyJobs, we'll use getJobs and client-side filter or just show recent
        const jobs = await api.getJobs().catch(() => []);

        // Mock applicants for now as we don't have an endpoint
        const applicants = [];

        dashboardData = {
            user,
            activeJobs: jobs.slice(0, 5), // Just show first 5 for now
            recentApplicants: applicants
        };

        renderUserInfo(user);
        renderQuickStats();
        renderRecentJobs(dashboardData.activeJobs);
        renderRecentApplicants(dashboardData.recentApplicants);

    } catch (error) {
        console.error('Error loading dashboard:', error);
        toast.error('Failed to load dashboard data');
    }
}

// ============================================
// SHOW LOADING STATES
// ============================================

function showLoadingStates() {
    // Check if elements exist before trying to show skeleton
    const recentJobsWidget = document.getElementById('recentJobsWidget');
    if (recentJobsWidget) showLoadingSkeleton(recentJobsWidget, 'card', 3);

    const recentApplicantsWidget = document.getElementById('recentApplicantsWidget');
    if (recentApplicantsWidget) showLoadingSkeleton(recentApplicantsWidget, 'card', 3);
}

// ============================================
// RENDER USER INFO
// ============================================

function renderUserInfo(user) {
    if (!user) return;

    const userName = document.getElementById('userName');
    const userInitials = document.getElementById('userInitials');

    if (userName) {
        userName.textContent = user.full_name || user.email.split('@')[0];
    }

    if (userInitials) {
        const initials = (user.full_name || user.email)
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
        userInitials.textContent = initials;
    }
}

// ============================================
// RENDER QUICK STATS
// ============================================

function renderQuickStats() {
    const stats = {
        activeJobsCount: dashboardData.activeJobs?.length || 0,
        totalApplicantsCount: 0, // Mocked
        interviewsScheduledCount: 0 // Mocked
    };

    Object.entries(stats).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            animateCounter(element, value);
        }
    });
}

// ============================================
// RENDER RECENT JOBS
// ============================================

function renderRecentJobs(jobs) {
    const container = document.getElementById('recentJobsWidget');
    if (!container) return;

    if (!jobs || jobs.length === 0) {
        container.innerHTML = `
            <div class="empty-state-small">
                <p class="empty-text">No active jobs</p>
                <p class="empty-subtext">Post a new job to find candidates</p>
                <button class="btn btn-primary btn-sm" onclick="window.location.href='post-job.html'">
                    Post a Job
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = jobs.map((job, index) => `
        <div class="job-card fade-in-up delay-${index * 100}">
            <div class="job-header">
                <div>
                    <h3 class="job-title">${job.title}</h3>
                    <p class="job-company">${job.location || 'Remote'} • ${formatDate(job.posted_at)}</p>
                </div>
                <div class="job-actions">
                    <button class="btn btn-outline btn-sm" onclick="viewJobApplications(${job.id})">
                        View Applicants
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================
// RENDER RECENT APPLICANTS
// ============================================

function renderRecentApplicants(applicants) {
    const container = document.getElementById('recentApplicantsWidget');
    if (!container) return;

    if (!applicants || applicants.length === 0) {
        container.innerHTML = `
            <div class="empty-state-small">
                <p class="empty-text">No recent applicants</p>
                <p class="empty-subtext">Applicants will appear here when they apply</p>
            </div>
        `;
        return;
    }
    // Render applicants logic would go here
}

// ============================================
// ACTIONS
// ============================================

function viewJobApplications(jobId) {
    window.location.href = `candidates.html?jobId=${jobId}`;
}

function setupEventListeners() {
    // Add any specific event listeners here
}

async function refreshDashboard() {
    await loadDashboard();
}
