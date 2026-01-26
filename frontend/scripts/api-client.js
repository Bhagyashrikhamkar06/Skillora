// API Client for backend communication
const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.auth !== false)
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth endpoints
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            auth: false,
            body: JSON.stringify({ email, password })
        });
    }

    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            auth: false,
            body: JSON.stringify(userData)
        });
    }

    async getProfile() {
        return this.request('/auth/profile');
    }

    async updateProfile(data) {
        return this.request('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // Interview endpoints
    async startInterview(jobRole, interviewType) {
        return this.request('/interview/start', {
            method: 'POST',
            body: JSON.stringify({ job_role: jobRole, interview_type: interviewType })
        });
    }

    async submitAnswer(sessionId, questionNumber, answer) {
        return this.request('/interview/answer', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                question_number: questionNumber,
                answer: answer
            })
        });
    }

    async completeInterview(sessionId) {
        return this.request(`/interview/${sessionId}/complete`, {
            method: 'POST'
        });
    }

    async endInterview(sessionId, feedback) {
        return this.request(`/interview/end/${sessionId}`, {
            method: 'POST',
            body: JSON.stringify({ feedback })
        });
    }

    async getInterviewHistory() {
        return this.request('/interview/history');
    }

    // Profile Analysis endpoints
    async extractProfileLinks(resumeText) {
        return this.request('/profile-analysis/extract', {
            method: 'POST',
            body: JSON.stringify({ resume_text: resumeText })
        });
    }

    async scrapeAndAnalyzeProfiles() {
        return this.request('/profile-analysis/scrape', {
            method: 'POST'
        });
    }

    async getProfileAnalysisReport() {
        return this.request('/profile-analysis/report', {
            method: 'GET'
        });
    }

    async updateProfileLinks(links) {
        return this.request('/profile-analysis/links', {
            method: 'PUT',
            body: JSON.stringify(links)
        });
    }

    async refreshProfileAnalysis() {
        return this.request('/profile-analysis/refresh', {
            method: 'POST'
        });
    }

    // Resume endpoints
    async uploadResume(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/resume/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        return response.json();
    }

    async getActiveResume() {
        return this.request('/resume/active');
    }

    async getAllResumes() {
        return this.request('/resume/');
    }

    // Jobs endpoints
    async getJobs(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/jobs/?${params}`);
    }

    async getJob(jobId) {
        return this.request(`/jobs/${jobId}`);
    }

    async createJob(jobData) {
        return this.request('/jobs/', {
            method: 'POST',
            body: JSON.stringify(jobData)
        });
    }

    async applyToJob(jobId, applicationData = {}) {
        return this.request(`/jobs/${jobId}/apply`, {
            method: 'POST',
            body: JSON.stringify(applicationData)
        });
    }

    async saveJob(jobId) {
        return this.request(`/jobs/${jobId}/save`, {
            method: 'POST'
        });
    }

    async getSavedJobs() {
        return this.request('/jobs/saved');
    }

    async getMyApplications() {
        return this.request('/jobs/my-applications');
    }

    // Recommendations endpoints
    async getRecommendations(limit = 20) {
        return this.request(`/recommendations/?limit=${limit}`);
    }

    async getSimilarJobs(jobId) {
        return this.request(`/recommendations/similar/${jobId}`);
    }

    // Interview endpoints
    async startInterview(jobRole, interviewType) {
        return this.request('/interview/start', {
            method: 'POST',
            body: JSON.stringify({ job_role: jobRole, interview_type: interviewType })
        });
    }

    async submitAnswer(sessionId, questionNumber, answer) {
        return this.request('/interview/answer', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                question_number: questionNumber,
                answer: answer
            })
        });
    }

    async completeInterview(sessionId) {
        return this.request(`/interview/${sessionId}/complete`, {
            method: 'POST'
        });
    }

    async getInterviewHistory() {
        return this.request('/interview/history');
    }
}

// Helper functions
function isAuthenticated() {
    return !!localStorage.getItem('token');
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Export for use in other scripts
window.APIClient = APIClient;
window.isAuthenticated = isAuthenticated;
window.getCurrentUser = getCurrentUser;
window.logout = logout;
window.requireAuth = requireAuth;
