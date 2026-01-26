/**
 * Jobs Search Page JavaScript
 */

const api = new APIClient();

// State management
let jobsState = {
    allJobs: [],
    filteredJobs: [],
    currentPage: 1,
    jobsPerPage: 12,
    filters: {
        search: '',
        location: [],
        locationCity: '',
        jobType: [],
        experience: [],
        salaryMin: null,
        salaryMax: null,
        postedDate: 'all'
    },
    sortBy: 'relevance'
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Load jobs
    await loadJobs();

    // Setup search with debouncing
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            jobsState.filters.search = e.target.value;
            applyFilters();
        }, 300));
    }

    // Initialize
    renderJobs();
});

// ============================================
// LOAD JOBS
// ============================================

async function loadJobs() {
    try {
        showLoadingSkeleton(document.getElementById('jobsContainer'), 'job', 6);

        const response = await api.getJobs();
        jobsState.allJobs = response.jobs || response || [];
        jobsState.filteredJobs = [...jobsState.allJobs];

        applyFilters();

    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('jobsContainer').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">😕</div>
                <p class="empty-text">Failed to load jobs</p>
                <p class="empty-subtext">${error.message}</p>
                <button class="btn btn-primary" onclick="loadJobs()">Retry</button>
            </div>
        `;
    }
}

// ============================================
// APPLY FILTERS
// ============================================

function applyFilters() {
    let filtered = [...jobsState.allJobs];

    // Search filter
    if (jobsState.filters.search) {
        const searchLower = jobsState.filters.search.toLowerCase();
        filtered = filtered.filter(job =>
            job.title?.toLowerCase().includes(searchLower) ||
            job.company_name?.toLowerCase().includes(searchLower) ||
            job.description?.toLowerCase().includes(searchLower) ||
            job.required_skills?.some(skill => skill.toLowerCase().includes(searchLower))
        );
    }

    // Location filter
    if (jobsState.filters.location.length > 0) {
        filtered = filtered.filter(job => {
            const location = job.location?.toLowerCase() || '';
            return jobsState.filters.location.some(loc => {
                if (loc === 'remote') return location.includes('remote');
                if (loc === 'hybrid') return location.includes('hybrid');
                if (loc === 'onsite') return !location.includes('remote') && !location.includes('hybrid');
                return false;
            });
        });
    }

    // Location city filter
    if (jobsState.filters.locationCity) {
        const city = jobsState.filters.locationCity.toLowerCase();
        filtered = filtered.filter(job =>
            job.location?.toLowerCase().includes(city)
        );
    }

    // Job type filter
    if (jobsState.filters.jobType.length > 0) {
        filtered = filtered.filter(job =>
            jobsState.filters.jobType.includes(job.job_type?.toLowerCase())
        );
    }

    // Experience filter
    if (jobsState.filters.experience.length > 0) {
        filtered = filtered.filter(job => {
            const exp = job.experience_required || 0;
            return jobsState.filters.experience.some(level => {
                if (level === 'entry') return exp <= 2;
                if (level === 'mid') return exp > 2 && exp <= 5;
                if (level === 'senior') return exp > 5;
                return false;
            });
        });
    }

    // Salary filter
    if (jobsState.filters.salaryMin) {
        filtered = filtered.filter(job =>
            (job.salary_max || job.salary_min || 0) >= jobsState.filters.salaryMin
        );
    }
    if (jobsState.filters.salaryMax) {
        filtered = filtered.filter(job =>
            (job.salary_min || job.salary_max || Infinity) <= jobsState.filters.salaryMax
        );
    }

    // Posted date filter
    if (jobsState.filters.postedDate !== 'all') {
        const now = new Date();
        const cutoffDays = {
            '24h': 1,
            '7d': 7,
            '30d': 30
        }[jobsState.filters.postedDate];

        if (cutoffDays) {
            const cutoffDate = new Date(now - cutoffDays * 24 * 60 * 60 * 1000);
            filtered = filtered.filter(job =>
                new Date(job.posted_at) >= cutoffDate
            );
        }
    }

    jobsState.filteredJobs = filtered;
    jobsState.currentPage = 1;

    applySort();
    updateActiveFilters();
    renderJobs();
}

// ============================================
// COLLECT FILTERS FROM UI
// ============================================

window.applyFilters = function () {
    // Collect location filters
    jobsState.filters.location = Array.from(
        document.querySelectorAll('input[name="location"]:checked')
    ).map(cb => cb.value);

    // Collect location city
    jobsState.filters.locationCity = document.getElementById('locationInput')?.value || '';

    // Collect job type filters
    jobsState.filters.jobType = Array.from(
        document.querySelectorAll('input[name="job_type"]:checked')
    ).map(cb => cb.value);

    // Collect experience filters
    jobsState.filters.experience = Array.from(
        document.querySelectorAll('input[name="experience"]:checked')
    ).map(cb => cb.value);

    // Collect salary filters
    jobsState.filters.salaryMin = parseInt(document.getElementById('salaryMin')?.value) || null;
    jobsState.filters.salaryMax = parseInt(document.getElementById('salaryMax')?.value) || null;

    // Collect posted date filter
    const postedDateChecked = document.querySelector('input[name="posted_date"]:checked');
    jobsState.filters.postedDate = postedDateChecked?.value || 'all';

    applyFilters();
};

// ============================================
// APPLY SORT
// ============================================

window.applySort = function () {
    const sortSelect = document.getElementById('sortSelect');
    jobsState.sortBy = sortSelect?.value || 'relevance';

    let sorted = [...jobsState.filteredJobs];

    switch (jobsState.sortBy) {
        case 'date':
            sorted.sort((a, b) => new Date(b.posted_at) - new Date(a.posted_at));
            break;
        case 'salary_high':
            sorted.sort((a, b) => (b.salary_max || 0) - (a.salary_max || 0));
            break;
        case 'salary_low':
            sorted.sort((a, b) => (a.salary_min || 0) - (b.salary_min || 0));
            break;
        case 'match_score':
            sorted.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
            break;
        case 'relevance':
        default:
            // Keep current order (relevance from backend)
            break;
    }

    jobsState.filteredJobs = sorted;
    renderJobs();
};

// ============================================
// UPDATE ACTIVE FILTERS DISPLAY
// ============================================

function updateActiveFilters() {
    const container = document.getElementById('activeFilters');
    if (!container) return;

    const chips = [];

    // Search chip
    if (jobsState.filters.search) {
        chips.push({
            label: `Search: "${jobsState.filters.search}"`,
            remove: () => {
                document.getElementById('searchInput').value = '';
                jobsState.filters.search = '';
                applyFilters();
            }
        });
    }

    // Location chips
    jobsState.filters.location.forEach(loc => {
        chips.push({
            label: `Location: ${loc}`,
            remove: () => {
                document.querySelector(`input[name="location"][value="${loc}"]`).checked = false;
                window.applyFilters();
            }
        });
    });

    // City chip
    if (jobsState.filters.locationCity) {
        chips.push({
            label: `City: ${jobsState.filters.locationCity}`,
            remove: () => {
                document.getElementById('locationInput').value = '';
                window.applyFilters();
            }
        });
    }

    // Job type chips
    jobsState.filters.jobType.forEach(type => {
        chips.push({
            label: `Type: ${type}`,
            remove: () => {
                document.querySelector(`input[name="job_type"][value="${type}"]`).checked = false;
                window.applyFilters();
            }
        });
    });

    // Experience chips
    jobsState.filters.experience.forEach(exp => {
        chips.push({
            label: `Experience: ${exp}`,
            remove: () => {
                document.querySelector(`input[name="experience"][value="${exp}"]`).checked = false;
                window.applyFilters();
            }
        });
    });

    // Salary chip
    if (jobsState.filters.salaryMin || jobsState.filters.salaryMax) {
        const min = jobsState.filters.salaryMin || 0;
        const max = jobsState.filters.salaryMax || '∞';
        chips.push({
            label: `Salary: $${min} - $${max}`,
            remove: () => {
                document.getElementById('salaryMin').value = '';
                document.getElementById('salaryMax').value = '';
                window.applyFilters();
            }
        });
    }

    // Posted date chip
    if (jobsState.filters.postedDate !== 'all') {
        const labels = {
            '24h': 'Last 24 hours',
            '7d': 'Last 7 days',
            '30d': 'Last 30 days'
        };
        chips.push({
            label: labels[jobsState.filters.postedDate],
            remove: () => {
                document.querySelector('input[name="posted_date"][value="all"]').checked = true;
                window.applyFilters();
            }
        });
    }

    if (chips.length === 0) {
        container.innerHTML = '';
        container.style.display = 'none';
    } else {
        container.style.display = 'flex';
        container.innerHTML = chips.map(chip => `
            <div class="filter-chip">
                <span>${chip.label}</span>
                <button class="filter-chip-remove" onclick='${chip.remove.toString().replace(/'/g, "\\'")}()'>×</button>
            </div>
        `).join('');
    }
}

// ============================================
// CLEAR ALL FILTERS
// ============================================

window.clearAllFilters = function () {
    // Clear checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);

    // Clear text inputs
    document.getElementById('searchInput').value = '';
    document.getElementById('locationInput').value = '';
    document.getElementById('salaryMin').value = '';
    document.getElementById('salaryMax').value = '';

    // Reset radio to 'all'
    document.querySelector('input[name="posted_date"][value="all"]').checked = true;

    // Reset state
    jobsState.filters = {
        search: '',
        location: [],
        locationCity: '',
        jobType: [],
        experience: [],
        salaryMin: null,
        salaryMax: null,
        postedDate: 'all'
    };

    applyFilters();
    toast.info('All filters cleared');
};

// ============================================
// RENDER JOBS
// ============================================

function renderJobs() {
    const container = document.getElementById('jobsContainer');
    const resultsCount = document.getElementById('resultsCount');

    // Update results count
    if (resultsCount) {
        resultsCount.textContent = `${jobsState.filteredJobs.length} jobs found`;
    }

    // Calculate pagination
    const startIndex = (jobsState.currentPage - 1) * jobsState.jobsPerPage;
    const endIndex = startIndex + jobsState.jobsPerPage;
    const jobsToShow = jobsState.filteredJobs.slice(startIndex, endIndex);

    // Render jobs
    if (jobsToShow.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <p class="empty-text">No jobs found</p>
                <p class="empty-subtext">Try adjusting your filters or search terms</p>
                <button class="btn btn-primary" onclick="clearAllFilters()">Clear Filters</button>
            </div>
        `;
    } else {
        container.innerHTML = jobsToShow.map((job, index) => `
            <div class="job-card hover-lift fade-in-up delay-${(index % 6) * 100}" data-job-id="${job.id}">
                <div class="job-header">
                    <div class="job-title-section">
                        <h3 class="job-title">${job.title}</h3>
                        <p class="job-company">${job.company_name}</p>
                    </div>
                    ${job.match_score ? `
                        <div class="match-score">
                            <div class="score-circle" style="--score: ${job.match_score}">
                                <span class="score-value">${Math.round(job.match_score)}%</span>
                            </div>
                            <span class="score-label">Match</span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="job-meta">
                    <span class="job-meta-item">📍 ${job.location || 'Remote'}</span>
                    <span class="job-meta-item">💰 ${formatSalary(job.salary_min, job.salary_max)}</span>
                    <span class="job-meta-item">⏰ ${formatDate(job.posted_at)}</span>
                    ${job.job_type ? `<span class="job-meta-item">💼 ${job.job_type}</span>` : ''}
                </div>
                
                <p class="job-description">${truncateText(job.description, 150)}</p>
                
                <div class="job-skills">
                    ${(job.required_skills || []).slice(0, 5).map(skill =>
            `<span class="skill-tag">${skill}</span>`
        ).join('')}
                    ${(job.required_skills?.length || 0) > 5 ? `<span class="skill-tag">+${job.required_skills.length - 5}</span>` : ''}
                </div>
                
                <div class="job-actions">
                    <button class="btn btn-primary" onclick="applyToJob(${job.id})">
                        Apply Now
                    </button>
                    <button class="btn btn-outline" onclick="saveJob(${job.id})">
                        💾 Save
                    </button>
                    <button class="btn btn-outline" onclick="viewJobDetails(${job.id})">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');
    }

    // Render pagination
    renderPagination();
}

// ============================================
// RENDER PAGINATION
// ============================================

function renderPagination() {
    const container = document.getElementById('pagination');
    if (!container) return;

    const totalPages = Math.ceil(jobsState.filteredJobs.length / jobsState.jobsPerPage);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    const pages = [];
    const maxVisible = 5;
    let startPage = Math.max(1, jobsState.currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);

    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }

    container.innerHTML = `
        <button 
            class="pagination-btn" 
            onclick="goToPage(${jobsState.currentPage - 1})"
            ${jobsState.currentPage === 1 ? 'disabled' : ''}
        >
            ← Previous
        </button>
        
        ${startPage > 1 ? `
            <button class="pagination-btn" onclick="goToPage(1)">1</button>
            ${startPage > 2 ? '<span class="pagination-ellipsis">...</span>' : ''}
        ` : ''}
        
        ${Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i).map(page => `
            <button 
                class="pagination-btn ${page === jobsState.currentPage ? 'active' : ''}" 
                onclick="goToPage(${page})"
            >
                ${page}
            </button>
        `).join('')}
        
        ${endPage < totalPages ? `
            ${endPage < totalPages - 1 ? '<span class="pagination-ellipsis">...</span>' : ''}
            <button class="pagination-btn" onclick="goToPage(${totalPages})">${totalPages}</button>
        ` : ''}
        
        <button 
            class="pagination-btn" 
            onclick="goToPage(${jobsState.currentPage + 1})"
            ${jobsState.currentPage === totalPages ? 'disabled' : ''}
        >
            Next →
        </button>
    `;
}

window.goToPage = function (page) {
    const totalPages = Math.ceil(jobsState.filteredJobs.length / jobsState.jobsPerPage);
    if (page < 1 || page > totalPages) return;

    jobsState.currentPage = page;
    renderJobs();
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

// ============================================
// JOB ACTIONS
// ============================================

window.performSearch = function () {
    const searchInput = document.getElementById('searchInput');
    jobsState.filters.search = searchInput.value;
    applyFilters();
};

async function applyToJob(jobId) {
    try {
        await api.applyToJob(jobId);
        toast.success('Application submitted successfully!');
    } catch (error) {
        toast.error(error.message || 'Failed to apply to job');
    }
}

async function saveJob(jobId) {
    try {
        await api.saveJob(jobId);
        toast.success('Job saved successfully!');
    } catch (error) {
        toast.error(error.message || 'Failed to save job');
    }
}

async function viewJobDetails(jobId) {
    const job = jobsState.allJobs.find(j => j.id === jobId);
    if (!job) return;

    document.getElementById('modalJobTitle').textContent = job.title;
    document.getElementById('jobDetailsContent').innerHTML = `
        <div class="job-details">
            <div class="job-details-header">
                <div>
                    <h3>${job.company_name}</h3>
                    <div class="job-meta" style="margin-top: 0.5rem;">
                        <span class="job-meta-item">📍 ${job.location || 'Remote'}</span>
                        <span class="job-meta-item">💰 ${formatSalary(job.salary_min, job.salary_max)}</span>
                        <span class="job-meta-item">⏰ ${formatDate(job.posted_at)}</span>
                    </div>
                </div>
                ${job.match_score ? `
                    <div class="match-score-large">
                        <div class="score-circle-large" style="--score: ${job.match_score}">
                            <span class="score-value-large">${Math.round(job.match_score)}%</span>
                        </div>
                        <span class="score-label">Match</span>
                    </div>
                ` : ''}
            </div>

            <div class="job-details-section">
                <h4>Job Description</h4>
                <p>${job.description}</p>
            </div>

            ${job.required_skills && job.required_skills.length > 0 ? `
                <div class="job-details-section">
                    <h4>Required Skills</h4>
                    <div class="job-skills">
                        ${job.required_skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                    </div>
                </div>
            ` : ''}

            ${job.requirements ? `
                <div class="job-details-section">
                    <h4>Requirements</h4>
                    <p>${job.requirements}</p>
                </div>
            ` : ''}

            ${job.benefits ? `
                <div class="job-details-section">
                    <h4>Benefits</h4>
                    <p>${job.benefits}</p>
                </div>
            ` : ''}

            <div class="job-details-actions">
                <button class="btn btn-primary btn-block" onclick="applyToJob(${job.id}); closeModal('jobDetailsModal')">
                    Apply Now
                </button>
                <button class="btn btn-outline btn-block" onclick="saveJob(${job.id})">
                    💾 Save Job
                </button>
            </div>
        </div>
    `;

    openModal('jobDetailsModal');
}
