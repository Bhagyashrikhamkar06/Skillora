/**
 * Profile Analysis Page JavaScript
 */

const api = new APIClient();
let problemsChart = null;

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    await loadProfileAnalysis();
    setupEventListeners();
});

function setupEventListeners() {
    const editLinksForm = document.getElementById('editLinksForm');
    if (editLinksForm) {
        editLinksForm.addEventListener('submit', handleEditLinksSubmit);
    }
}

// ============================================
// LOAD PROFILE ANALYSIS
// ============================================

async function loadProfileAnalysis() {
    try {
        showLoadingSkeleton(document.getElementById('profileLinksGrid'), 'card', 2);
        showLoadingSkeleton(document.getElementById('githubStats'), 'text', 4);
        showLoadingSkeleton(document.getElementById('leetcodeStats'), 'text', 4);

        const report = await api.getProfileAnalysisReport();

        if (!report || !report.profile) {
            showEmptyState();
            return;
        }

        renderProfileLinks(report.profile);
        renderOverallScore(report);
        renderGitHubAnalysis(report);
        renderLeetCodeAnalysis(report);
        renderRecommendations(report.recommendations || []);
        renderTopRepositories(report.profile.github_data);

    } catch (error) {
        console.error('Error loading profile analysis:', error);
        if (error.message.includes('No profile analysis found')) {
            showEmptyState();
        } else {
            toast.error('Failed to load profile analysis');
        }
    }
}

function showEmptyState() {
    document.querySelector('.profile-analysis-header').innerHTML += `
        <div class="empty-state">
            <div class="empty-icon">🔗</div>
            <p class="empty-text">No profile analysis found</p>
            <p class="empty-subtext">Add your GitHub and LeetCode profiles to get started</p>
            <button class="btn btn-primary" onclick="openEditLinksModal()">Add Profile Links</button>
        </div>
    `;
}

// ============================================
// RENDER PROFILE LINKS
// ============================================

function renderProfileLinks(profile) {
    const container = document.getElementById('profileLinksGrid');

    const links = [
        {
            platform: 'GitHub',
            icon: '🐙',
            username: profile.github_username,
            url: profile.github_username ? `https://github.com/${profile.github_username}` : null
        },
        {
            platform: 'LeetCode',
            icon: '💻',
            username: profile.leetcode_username,
            url: profile.leetcode_username ? `https://leetcode.com/${profile.leetcode_username}` : null
        },
        {
            platform: 'LinkedIn',
            icon: '💼',
            username: profile.linkedin_url ? 'Connected' : null,
            url: profile.linkedin_url ? `https://${profile.linkedin_url}` : null
        },
        {
            platform: 'Portfolio',
            icon: '🌐',
            username: profile.portfolio_url ? 'Connected' : null,
            url: profile.portfolio_url
        }
    ];

    container.innerHTML = links.map(link => `
        <div class="profile-link-card ${link.username ? 'connected' : 'disconnected'}">
            <div class="profile-link-icon">${link.icon}</div>
            <div class="profile-link-info">
                <h4>${link.platform}</h4>
                ${link.username ? `
                    <p class="profile-link-username">${link.username}</p>
                    ${link.url ? `<a href="${link.url}" target="_blank" class="profile-link-url">View Profile →</a>` : ''}
                ` : `
                    <p class="profile-link-status">Not connected</p>
                `}
            </div>
        </div>
    `).join('');
}

// ============================================
// RENDER OVERALL SCORE
// ============================================

function renderOverallScore(report) {
    const overallScore = report.overall_score || 0;
    const githubScore = report.profile.github_score || 0;
    const leetcodeScore = report.profile.leetcode_score || 0;

    // Animate overall score
    const scoreCircle = document.getElementById('overallScoreCircle');
    const scoreValue = document.getElementById('overallScoreValue');

    scoreCircle.style.setProperty('--score', overallScore);
    animateCounter(scoreValue, overallScore);

    // Update platform scores
    animateCounter(document.getElementById('githubScore'), githubScore);
    animateCounter(document.getElementById('leetcodeScore'), leetcodeScore);

    // Update description
    const description = getScoreDescription(overallScore);
    document.getElementById('scoreDescription').textContent = description;
}

function getScoreDescription(score) {
    if (score >= 80) return '🌟 Excellent! Your profile is highly competitive.';
    if (score >= 60) return '✅ Good! You have a strong foundation.';
    if (score >= 40) return '📈 Moderate. Focus on the recommendations below.';
    if (score >= 20) return '⚠️ Needs improvement. Follow the action items.';
    return '🚀 Getting started. Build your profile with our recommendations.';
}

// ============================================
// RENDER GITHUB ANALYSIS
// ============================================

function renderGitHubAnalysis(report) {
    const githubData = report.profile.github_data;
    const githubAnalysis = report.github_analysis;

    if (!githubData || githubData.error) {
        document.getElementById('githubUsername').textContent = 'Not connected or error';
        document.getElementById('githubStats').innerHTML = '<p class="error-text">Unable to load GitHub data</p>';
        return;
    }

    document.getElementById('githubUsername').textContent = `@${githubData.username}`;

    // Render stats
    const stats = [
        { label: 'Repositories', value: githubData.public_repos || 0, icon: '📦' },
        { label: 'Total Stars', value: githubData.total_stars || 0, icon: '⭐' },
        { label: 'Followers', value: githubData.followers || 0, icon: '👥' },
        { label: 'Languages', value: githubData.top_languages?.length || 0, icon: '💻' }
    ];

    document.getElementById('githubStats').innerHTML = stats.map(stat => `
        <div class="stat-item">
            <span class="stat-icon">${stat.icon}</span>
            <div>
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            </div>
        </div>
    `).join('');

    // Render insights
    if (githubAnalysis) {
        renderInsights('githubStrengths', githubAnalysis.strengths || []);
        renderInsights('githubImprovements', githubAnalysis.improvements || []);
    }
}

// ============================================
// RENDER LEETCODE ANALYSIS
// ============================================

function renderLeetCodeAnalysis(report) {
    const leetcodeData = report.profile.leetcode_data;
    const leetcodeAnalysis = report.leetcode_analysis;

    if (!leetcodeData || leetcodeData.error) {
        document.getElementById('leetcodeUsername').textContent = 'Not connected or error';
        document.getElementById('leetcodeStats').innerHTML = '<p class="error-text">Unable to load LeetCode data</p>';
        return;
    }

    document.getElementById('leetcodeUsername').textContent = `@${leetcodeData.username}`;

    const problems = leetcodeData.problems_solved || {};

    // Render stats
    const stats = [
        { label: 'Total Solved', value: problems.total || 0, icon: '✅' },
        { label: 'Easy', value: problems.easy || 0, icon: '🟢' },
        { label: 'Medium', value: problems.medium || 0, icon: '🟡' },
        { label: 'Hard', value: problems.hard || 0, icon: '🔴' }
    ];

    document.getElementById('leetcodeStats').innerHTML = stats.map(stat => `
        <div class="stat-item">
            <span class="stat-icon">${stat.icon}</span>
            <div>
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            </div>
        </div>
    `).join('');

    // Render chart
    renderProblemsChart(problems);

    // Render insights
    if (leetcodeAnalysis) {
        renderInsights('leetcodeStrengths', leetcodeAnalysis.strengths || []);
        renderInsights('leetcodeImprovements', leetcodeAnalysis.improvements || []);
    }
}

function renderProblemsChart(problems) {
    const ctx = document.getElementById('problemsChart');
    if (!ctx) return;

    // Destroy existing chart
    if (problemsChart) {
        problemsChart.destroy();
    }

    problemsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Easy', 'Medium', 'Hard'],
            datasets: [{
                data: [
                    problems.easy || 0,
                    problems.medium || 0,
                    problems.hard || 0
                ],
                backgroundColor: [
                    '#10b981',
                    '#f59e0b',
                    '#ef4444'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#cbd5e1',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#475569',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true
                }
            }
        }
    });
}

// ============================================
// RENDER INSIGHTS
// ============================================

function renderInsights(elementId, insights) {
    const container = document.getElementById(elementId);
    if (!container) return;

    if (insights.length === 0) {
        container.innerHTML = '<li class="insight-empty">No insights available</li>';
        return;
    }

    container.innerHTML = insights.map(insight => `
        <li class="insight-item">${insight}</li>
    `).join('');
}

// ============================================
// RENDER RECOMMENDATIONS
// ============================================

function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');

    if (recommendations.length === 0) {
        container.innerHTML = `
            <div class="empty-state-small">
                <p>No recommendations available yet. Complete your profile analysis first.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = recommendations.map((rec, index) => `
        <div class="recommendation-card fade-in-up delay-${index * 100}">
            <div class="recommendation-header">
                <span class="priority-badge priority-${rec.priority?.toLowerCase() || 'medium'}">
                    ${rec.priority || 'Medium'} Priority
                </span>
                <span class="timeline-badge">${rec.timeline || 'Ongoing'}</span>
            </div>
            <h4 class="recommendation-action">${rec.action}</h4>
            <p class="recommendation-impact">💡 Impact: ${rec.impact}</p>
        </div>
    `).join('');
}

// ============================================
// RENDER TOP REPOSITORIES
// ============================================

function renderTopRepositories(githubData) {
    if (!githubData || !githubData.top_repos || githubData.top_repos.length === 0) {
        return;
    }

    const section = document.getElementById('repositoriesSection');
    const container = document.getElementById('repositoriesList');

    section.style.display = 'block';

    container.innerHTML = githubData.top_repos.map(repo => `
        <div class="repo-card">
            <h4 class="repo-name">
                <a href="${repo.url}" target="_blank">${repo.name}</a>
            </h4>
            <p class="repo-description">${repo.description || 'No description'}</p>
            <div class="repo-stats">
                <span class="repo-stat">⭐ ${repo.stars}</span>
                <span class="repo-stat">🔱 ${repo.forks}</span>
                ${repo.language ? `<span class="repo-stat">💻 ${repo.language}</span>` : ''}
            </div>
        </div>
    `).join('');
}

// ============================================
// EDIT LINKS MODAL
// ============================================

window.openEditLinksModal = async function () {
    try {
        const report = await api.getProfileAnalysisReport();
        const profile = report.profile;

        document.getElementById('editGithubUsername').value = profile.github_username || '';
        document.getElementById('editLeetcodeUsername').value = profile.leetcode_username || '';
        document.getElementById('editLinkedinUrl').value = profile.linkedin_url || '';
        document.getElementById('editPortfolioUrl').value = profile.portfolio_url || '';
    } catch (error) {
        // Empty form for new users
    }

    openModal('editLinksModal');
};

async function handleEditLinksSubmit(e) {
    e.preventDefault();

    const links = {
        github_username: document.getElementById('editGithubUsername').value.trim(),
        leetcode_username: document.getElementById('editLeetcodeUsername').value.trim(),
        linkedin_url: document.getElementById('editLinkedinUrl').value.trim(),
        portfolio_url: document.getElementById('editPortfolioUrl').value.trim()
    };

    try {
        toast.info('Updating profile links...');
        await api.updateProfileLinks(links);

        toast.success('Profile links updated! Analyzing...');
        closeModal('editLinksModal');

        // Trigger analysis
        await api.scrapeAndAnalyzeProfiles();

        toast.success('Analysis complete!');
        await loadProfileAnalysis();

    } catch (error) {
        toast.error(error.message || 'Failed to update profile links');
    }
}

// ============================================
// REFRESH ANALYSIS
// ============================================

window.refreshAnalysis = async function () {
    try {
        toast.info('Refreshing analysis... This may take a moment.');

        await api.refreshProfileAnalysis();

        toast.success('Analysis refreshed successfully!');
        await loadProfileAnalysis();

    } catch (error) {
        toast.error(error.message || 'Failed to refresh analysis');
    }
};
