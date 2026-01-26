# AI-Powered Job Recommendation and Career Assistance Platform

A comprehensive job portal with intelligent resume parsing, AI-driven job matching, and mock interview preparation.

## 🚀 Features

- **Smart Resume Parser**: NLP-based skill extraction and ATS scoring
- **Intelligent Job Matching**: TF-IDF and cosine similarity for accurate recommendations
- **Explainable AI**: Understand why jobs match your profile
- **AI Mock Interviews**: Practice with AI-generated questions and get detailed feedback
- **Job Management**: Post, search, and apply to jobs
- **Career Guidance**: Skill gap analysis and learning recommendations

## 🛠️ Tech Stack

**Backend:**
- Python 3.10+
- Flask (REST API)
- PostgreSQL (structured data)
- MongoDB (document storage)
- spaCy (NLP)
- scikit-learn (ML)
- OpenAI GPT-4 (AI interviews)

**Frontend:**
- HTML5, CSS3, JavaScript
- Modern, responsive design

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL 15+
- MongoDB 6.0+ (optional)
- OpenAI API key

## 🔧 Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd Project
```

### 2. Set up Python virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Download spaCy model
```bash
python -m spacy download en_core_web_sm
```

### 5. Set up database
```bash
# Create PostgreSQL database
createdb job_portal

# Run schema
psql job_portal < ../database/schema.sql
```

### 6. Configure environment variables
```bash
# Copy example env file
cp ../.env.example ../.env

# Edit .env and add your credentials:
# - DATABASE_URL
# - OPENAI_API_KEY
# - SECRET_KEY
# - JWT_SECRET_KEY
```

## 🚀 Running the Application

### Start Backend
```bash
cd backend
python app.py
```

The API will be available at `http://localhost:5000`

### Start Frontend
Simply open `frontend/index.html` in your browser, or use a local server:
```bash
cd frontend
python -m http.server 8000
```

Then visit `http://localhost:8000`

## 📚 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

### Resume
- `POST /api/resume/upload` - Upload and parse resume
- `GET /api/resume/active` - Get active resume
- `GET /api/resume/` - Get all resumes
- `DELETE /api/resume/<id>` - Delete resume

### Jobs
- `POST /api/jobs/` - Create job (recruiter only)
- `GET /api/jobs/` - List jobs with filters
- `GET /api/jobs/<id>` - Get job details
- `POST /api/jobs/<id>/apply` - Apply to job
- `POST /api/jobs/<id>/save` - Save job
- `GET /api/jobs/saved` - Get saved jobs

### Recommendations
- `GET /api/recommendations/` - Get personalized recommendations
- `GET /api/recommendations/similar/<id>` - Get similar jobs

### Interview
- `POST /api/interview/start` - Start interview session
- `POST /api/interview/answer` - Submit answer
- `POST /api/interview/<id>/complete` - Complete interview
- `GET /api/interview/history` - Get interview history

## 🎯 Usage

### For Job Seekers
1. Register and login
2. Upload your resume (PDF/DOCX)
3. View personalized job recommendations
4. Apply to jobs
5. Practice with AI mock interviews

### For Recruiters
1. Register as recruiter
2. Post job openings
3. View applicants
4. Manage job postings

## 🧪 Testing

```bash
cd backend
pytest tests/
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- Rate limiting on API endpoints
- CORS configuration

## 📝 License

This project is for educational purposes.

## 👥 Contributors

- Your Name

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- OpenAI for AI interview system
- scikit-learn for recommendation engine
