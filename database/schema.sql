-- AI-Powered Job Recommendation Platform Database Schema
-- PostgreSQL

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('job_seeker', 'recruiter')),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    location VARCHAR(255),
    profile_photo_url TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP
);

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_path TEXT,
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_data JSONB,
    total_experience_months INTEGER,
    quality_score NUMERIC(3,2),
    is_active BOOLEAN DEFAULT TRUE
);

-- Skills table
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    skill_name VARCHAR(100),
    skill_category VARCHAR(50),
    proficiency_level VARCHAR(20),
    years_of_experience NUMERIC(3,1)
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    recruiter_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    description TEXT,
    required_skills TEXT[],
    experience_min INTEGER,
    experience_max INTEGER,
    location VARCHAR(255),
    job_type VARCHAR(50),
    salary_min NUMERIC(10,2),
    salary_max NUMERIC(10,2),
    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    source VARCHAR(50) DEFAULT 'internal',
    external_url TEXT,
    view_count INTEGER DEFAULT 0
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(id),
    status VARCHAR(20) DEFAULT 'pending',
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cover_letter TEXT,
    match_score NUMERIC(5,2),
    UNIQUE(user_id, job_id)
);

-- Saved jobs table
CREATE TABLE IF NOT EXISTS saved_jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);

-- Interview sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_role VARCHAR(255),
    interview_type VARCHAR(50),
    difficulty_level VARCHAR(20),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_questions INTEGER,
    overall_score NUMERIC(4,2),
    performance_level VARCHAR(20),
    feedback_summary TEXT
);

-- Interview Q&A table
CREATE TABLE IF NOT EXISTS interview_qa (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_number INTEGER,
    question TEXT,
    user_answer TEXT,
    model_answer TEXT,
    score NUMERIC(3,1),
    technical_correctness NUMERIC(3,1),
    clarity_score NUMERIC(3,1),
    relevance_score NUMERIC(3,1),
    feedback TEXT,
    strengths TEXT,
    improvements TEXT,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id);
