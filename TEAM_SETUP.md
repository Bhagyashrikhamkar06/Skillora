# Team Setup Guide - Skillora

## 🎯 Quick Start for Team Members

### Prerequisites Checklist

Before you begin, make sure you have:

- [ ] Git installed ([Download](https://git-scm.com/downloads))
- [ ] Python 3.10+ installed ([Download](https://www.python.org/downloads/))
- [ ] PostgreSQL 15+ installed ([Download](https://www.postgresql.org/download/))
- [ ] GitHub account with access to the repository
- [ ] SSH key added to GitHub ([Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh))

### Step-by-Step Setup

#### 1️⃣ Clone the Repository

```bash
git clone git@github.com:Bhagyashrikhamkar06/Skillora.git
cd Skillora
```

#### 2️⃣ Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cd ..
```

#### 4️⃣ Set Up PostgreSQL Database

```bash
# Create database
createdb job_portal

# Import schema
psql job_portal < database/schema.sql
```

> **Note:** If you don't have PostgreSQL installed, download it from [postgresql.org](https://www.postgresql.org/download/)

#### 5️⃣ Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# Use any text editor (VS Code, Notepad++, etc.)
```

**Required configurations in `.env`:**
- Update `DATABASE_URL` with your PostgreSQL credentials
- Add your `OPENAI_API_KEY` (get it from [OpenAI](https://platform.openai.com/api-keys))
- Generate secure keys for `SECRET_KEY` and `JWT_SECRET_KEY`

#### 6️⃣ Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 8000
```

**Access the application:**
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000

## 🔧 Common Setup Issues

### Issue: `psycopg2` installation fails

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Find process using port 5000 (Linux/Mac)
lsof -ti:5000 | xargs kill -9
```

### Issue: spaCy model not found

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: Database connection error

**Solution:**
- Check if PostgreSQL is running
- Verify `DATABASE_URL` in `.env` file
- Ensure database `job_portal` exists

## 👥 Team Collaboration Guidelines

### Adding Team Members to GitHub

1. Go to: https://github.com/Bhagyashrikhamkar06/Skillora/settings/access
2. Click "Add people"
3. Enter their GitHub username
4. Choose permission level (Write for developers)

### Working on Features

```bash
# 1. Always start from main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit
git add .
git commit -m "feat: description of your changes"

# 4. Push to GitHub
git push origin feature/your-feature-name

# 5. Create Pull Request on GitHub
```

### Before Submitting Pull Request

- [ ] Code runs without errors
- [ ] Tested all changes locally
- [ ] Followed code style guidelines
- [ ] Updated documentation if needed
- [ ] No sensitive data in commits

## 📂 Project Structure Overview

```
Skillora/
├── backend/              # Python Flask backend
│   ├── app.py           # Main application entry
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── utils/           # Helper functions
├── frontend/            # HTML/CSS/JS frontend
│   ├── index.html       # Landing page
│   ├── jobs.html        # Jobs listing
│   ├── styles/          # CSS files
│   └── scripts/         # JavaScript files
├── database/            # Database schemas
├── uploads/             # User uploads
└── .env                 # Environment variables (DO NOT COMMIT!)
```

## 🎓 Learning Resources

### For Backend Development
- [Flask Tutorial](https://flask.palletsprojects.com/en/latest/tutorial/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [Python Best Practices](https://docs.python-guide.org/)

### For Frontend Development
- [MDN Web Docs](https://developer.mozilla.org/)
- [JavaScript.info](https://javascript.info/)
- [CSS Tricks](https://css-tricks.com/)

### For Git & GitHub
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

## 💬 Getting Help

- **Technical Issues:** Create an issue on GitHub
- **Questions:** Ask in team chat or create a discussion
- **Bugs:** Report with detailed steps to reproduce

## 🚀 Next Steps

1. Complete the setup above
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines
3. Check GitHub Issues for tasks to work on
4. Join team communication channels
5. Start contributing!

---

**Welcome to the team! Happy coding! 🎉**
