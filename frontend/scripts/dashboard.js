/**
 * Dashboard JavaScript - Handle all dashboard interactions
 */

const api = new APIClient();
let dashboardData = {
    user: null,
    recommendations: [],
    applications: [],
    savedJobs: [],
    interviews: [],
    resume: null
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

        // Load all data in parallel
        // We use catch to return default values so one failure doesn't break everything
        const [
            userData,
            recommendationsData,
            applicationsData,
            savedJobsData,
            interviewsData,
            resumeData
        ] = await Promise.all([
            api.getProfile().catch(e => { console.error('Profile error:', e); return null; }),
            api.getRecommendations(5).catch(e => { console.error('Recs error:', e); return { recommendations: [] }; }),
            api.getMyApplications().catch(e => { console.error('Apps error:', e); return { applications: [] }; }),
            api.getSavedJobs().catch(e => { console.error('Saved error:', e); return { jobs: [] }; }),
            api.getInterviewHistory().catch(e => { console.error('Interview error:', e); return { sessions: [] }; }),
            api.getActiveResume().catch(e => { console.error('Resume error:', e); return null; })
        ]);

        // Unpack data from API responses (which are wrapper objects like { user: ... })
        const user = userData ? userData.user : null;
        const recommendations = recommendationsData ? (recommendationsData.recommendations || []) : [];
        const applications = applicationsData ? (applicationsData.applications || []) : [];
        const savedJobs = savedJobsData ? (savedJobsData.jobs || []) : [];
        const interviews = interviewsData ? (interviewsData.sessions || []) : [];
        const resume = resumeData ? resumeData.resume : null;

        // Store data
        dashboardData = { user, recommendations, applications, savedJobs, interviews, resume };

        // Render all sections
        renderUserInfo(user);
        renderQuickStats();
        renderRecommendations(recommendations);
        renderApplications(applications);
        renderSavedJobs(savedJobs);
        renderInterviews(interviews);
        renderResumeStatus(resume);

    } catch (error) {
        console.error('Error loading dashboard:', error);
        toast.error(`Dashboard Load Error: ${error.message}`);

        // Show error states in widgets to remove skeletons
        const widgets = ['recommendationsWidget', 'applicationsWidget', 'savedJobsWidget', 'interviewWidget', 'resumeWidget'];
        widgets.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = '<div class="error-state"><p>Failed to load data.</p></div>';
        });
    }
}

// ============================================
// SHOW LOADING STATES
// ============================================

function showLoadingStates() {
    showLoadingSkeleton(document.getElementById('recommendationsWidget'), 'job', 3);
    showLoadingSkeleton(document.getElementById('applicationsWidget'), 'card', 3);
    showLoadingSkeleton(document.getElementById('savedJobsWidget'), 'card', 2);
    showLoadingSkeleton(document.getElementById('interviewWidget'), 'card', 2);
    showLoadingSkeleton(document.getElementById('resumeWidget'), 'card', 1);
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
        recommendationsCount: dashboardData.recommendations?.length || 0,
        applicationsCount: dashboardData.applications?.length || 0,
        savedJobsCount: dashboardData.savedJobs?.length || 0,
        interviewsCount: dashboardData.interviews?.length || 0
    };

    Object.entries(stats).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            animateCounter(element, value);
        }
    });
}

// ============================================
// RENDER JOB RECOMMENDATIONS
// ============================================

function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendationsWidget');

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🎯</div>
                <p class="empty-text">No recommendations yet</p>
                <p class="empty-subtext">Upload your resume to get personalized job matches</p>
                <button class="btn btn-primary" onclick="openModal('uploadResumeModal')">
                    Upload Resume
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = recommendations.map((job, index) => `
        <div class="job-card hover-lift fade-in-up delay-${index * 100}" data-job-id="${job.id}">
            <div class="job-header">
                <div class="job-title-section">
                    <h3 class="job-title">${job.title}</h3>
                    <p class="job-company">${job.company_name}</p>
                </div>
                <div class="match-score">
                    <div class="score-circle" style="--score: ${job.match_score || 0}">
                        <span class="score-value">${Math.round(job.match_score || 0)}%</span>
                    </div>
                    <span class="score-label">Match</span>
                </div>
            </div>
            
            <div class="job-meta">
                <span class="job-meta-item">📍 ${job.location || 'Remote'}</span>
                <span class="job-meta-item">💰 ${formatSalary(job.salary_min, job.salary_max)}</span>
                <span class="job-meta-item">⏰ ${formatDate(job.posted_at)}</span>
            </div>
            
            <p class="job-description">${truncateText(job.description, 150)}</p>
            
            <div class="job-skills">
                ${(job.required_skills || []).slice(0, 4).map(skill =>
        `<span class="skill-tag">${skill}</span>`
    ).join('')}
                ${(job.required_skills?.length || 0) > 4 ? `<span class="skill-tag">+${job.required_skills.length - 4}</span>` : ''}
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
            
            ${job.match_explanation ? `
                <div class="match-explanation">
                    <strong>Why this matches:</strong> ${job.match_explanation}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// ============================================
// RENDER APPLICATIONS
// ============================================

function renderApplications(applications) {
    const container = document.getElementById('applicationsWidget');

    if (!applications || applications.length === 0) {
        container.innerHTML = `
            <div class="empty-state-small">
                <p class="empty-text">No applications yet</p>
                <p class="empty-subtext">Start applying to jobs to track your progress</p>
            </div>
        `;
        return;
    }

    const statusColors = {
        'pending': '#f59e0b',
        'reviewing': '#3b82f6',
        'interview': '#8b5cf6',
        'accepted': '#10b981',
        'rejected': '#ef4444'
    };

    const statusIcons = {
        'pending': '⏳',
        'reviewing': '👀',
        'interview': '🎤',
        'accepted': '✅',
        'rejected': '❌'
    };

    container.innerHTML = applications.slice(0, 5).map((app, index) => `
        <div class="application-card fade-in-up delay-${index * 100}">
            <div class="application-header">
                <div>
                    <h4 class="application-title">${app.job_title}</h4>
                    <p class="application-company">${app.company_name}</p>
                </div>
                <span class="status-badge" style="background: ${statusColors[app.status]}20; color: ${statusColors[app.status]}">
                    ${statusIcons[app.status]} ${app.status}
                </span>
            </div>
            <div class="application-meta">
                <span>Applied ${formatDate(app.applied_at)}</span>
            </div>
            <div class="application-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${getApplicationProgress(app.status)}%; background: ${statusColors[app.status]}"></div>
                </div>
            </div>
        </div>
    `).join('');
}

function getApplicationProgress(status) {
    const progress = {
        'pending': 25,
        'reviewing': 50,
        'interview': 75,
        'accepted': 100,
        'rejected': 100
    };
    return progress[status] || 0;
}

// ============================================
// RENDER SAVED JOBS
// ============================================

function renderSavedJobs(savedJobs) {
    const container = document.getElementById('savedJobsWidget');

    if (!savedJobs || savedJobs.length === 0) {
        container.innerHTML = `
            <div class="empty-state-small">
                <p class="empty-text">No saved jobs</p>
                <p class="empty-subtext">Save jobs to review them later</p>
            </div>
        `;
        return;
    }

    container.innerHTML = savedJobs.slice(0, 3).map((job, index) => `
        <div class="saved-job-item fade-in-up delay-${index * 100}" onclick="viewJobDetails(${job.job_id})">
            <div class="saved-job-info">
                <h4 class="saved-job-title">${job.job_title}</h4>
                <p class="saved-job-company">${job.company_name}</p>
                <span class="saved-job-date">Saved ${formatDate(job.saved_at)}</span>
            </div>
            <button class="btn-icon" onclick="event.stopPropagation(); unsaveJob(${job.job_id})" title="Remove">
                ×
            </button>
        </div>
    `).join('');
}

// ============================================
// RENDER INTERVIEWS
// ============================================

function renderInterviews(interviews) {
    const container = document.getElementById('interviewWidget');

    if (!interviews || interviews.length === 0) {
        container.innerHTML = `
            <div class="empty-state-small">
                <p class="empty-text">No interview practice yet</p>
                <button class="btn btn-primary btn-sm" onclick="window.location.href='interview.html'">
                    Start Practice
                </button>
            </div>
        `;
        return;
    }

    const latestInterview = interviews[0];
    container.innerHTML = `
        <div class="interview-summary fade-in-up">
            <div class="interview-stat">
                <span class="interview-stat-value">${interviews.length}</span>
                <span class="interview-stat-label">Sessions</span>
            </div>
            <div class="interview-stat">
                <span class="interview-stat-value">${latestInterview.score || 'N/A'}</span>
                <span class="interview-stat-label">Latest Score</span>
            </div>
        </div>
        <div class="interview-latest">
            <p class="interview-latest-title">Latest: ${latestInterview.job_role}</p>
            <p class="interview-latest-date">${formatDate(latestInterview.created_at)}</p>
        </div>
        <button class="btn btn-primary btn-block" onclick="window.location.href='interview.html'">
            Practice More
        </button>
    `;
}

// ============================================
// RENDER RESUME STATUS
// ============================================

function renderResumeStatus(resume) {
    const container = document.getElementById('resumeWidget');

    if (!resume) {
        container.innerHTML = `
            <div class="empty-state-small">
                <p class="empty-text">No resume uploaded</p>
                <button class="btn btn-primary btn-sm" onclick="openModal('uploadResumeModal')">
                    Upload Resume
                </button>
            </div>
        `;
        return;
    }

    const atsScore = resume.ats_score || 0;
    const scoreColor = atsScore >= 80 ? '#10b981' : atsScore >= 60 ? '#f59e0b' : '#ef4444';

    container.innerHTML = `
        <div class="resume-status fade-in-up">
            <div class="resume-info">
                <h4 class="resume-filename">${resume.filename || 'Resume.pdf'}</h4>
                <p class="resume-date">Uploaded ${formatDate(resume.uploaded_at)}</p>
            </div>
            <div class="ats-score" style="border-color: ${scoreColor}">
                <div class="ats-score-value" style="color: ${scoreColor}">${atsScore}</div>
                <div class="ats-score-label">ATS Score</div>
            </div>
        </div>
        <div class="resume-skills">
            <strong>Skills Found:</strong>
            <div class="skills-list">
                ${(resume.skills || []).slice(0, 5).map(skill =>
        `<span class="skill-tag-small">${skill}</span>`
    ).join('')}
                ${(resume.skills?.length || 0) > 5 ? `<span class="skill-tag-small">+${resume.skills.length - 5}</span>` : ''}
            </div>
        </div>
        <button class="btn btn-outline btn-block btn-sm" onclick="openModal('uploadResumeModal')">
            Upload New Resume
        </button>
    `;
}

// ============================================
// JOB ACTIONS
// ============================================

async function applyToJob(jobId) {
    try {
        await api.applyToJob(jobId);
        toast.success('Application submitted successfully!');
        await refreshDashboard();
    } catch (error) {
        toast.error(error.message || 'Failed to apply to job');
    }
}

async function saveJob(jobId) {
    try {
        await api.saveJob(jobId);
        toast.success('Job saved successfully!');
        await refreshDashboard();
    } catch (error) {
        toast.error(error.message || 'Failed to save job');
    }
}

async function unsaveJob(jobId) {
    try {
        // Assuming there's an unsave endpoint
        await api.request(`/jobs/${jobId}/unsave`, { method: 'DELETE' });
        toast.success('Job removed from saved');
        await refreshDashboard();
    } catch (error) {
        toast.error(error.message || 'Failed to remove job');
    }
}

function viewJobDetails(jobId) {
    window.location.href = `job-details.html?id=${jobId}`;
}

// ============================================
// RESUME UPLOAD
// ============================================

function setupEventListeners() {
    const resumeInput = document.getElementById('resumeInput');
    const uploadArea = document.getElementById('uploadArea');

    if (resumeInput) {
        resumeInput.addEventListener('change', handleResumeUpload);
    }

    if (uploadArea) {
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleResumeFile(files[0]);
            }
        });
    }

    // Hash navigation for quick actions
    if (window.location.hash === '#upload-resume') {
        openModal('uploadResumeModal');
    }
}

async function handleResumeUpload(event) {
    const file = event.target.files[0];
    if (file) {
        await handleResumeFile(file);
    }
}

async function handleResumeFile(file) {
    // Validate file
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type)) {
        toast.error('Please upload a PDF or Word document');
        return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB
        toast.error('File size must be less than 10MB');
        return;
    }

    try {
        // Show progress
        document.getElementById('uploadProgress').style.display = 'block';
        const progressBar = document.querySelector('#uploadProgress .progress-fill');

        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                progressBar.style.width = `${progress}%`;
            }
        }, 200);

        // Upload resume
        const result = await api.uploadResume(file);

        clearInterval(progressInterval);
        progressBar.style.width = '100%';

        setTimeout(() => {
            closeModal('uploadResumeModal');
            document.getElementById('uploadProgress').style.display = 'none';
            progressBar.style.width = '0%';
            toast.success('Resume uploaded and analyzed successfully!');
            refreshDashboard();
        }, 500);

    } catch (error) {
        document.getElementById('uploadProgress').style.display = 'none';
        toast.error(error.message || 'Failed to upload resume');
    }
}

// ============================================
// REFRESH DASHBOARD
// ============================================

async function refreshDashboard() {
    await loadDashboard();
}
