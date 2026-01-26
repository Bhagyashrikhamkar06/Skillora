# Contributing to Skillora

Welcome to the Skillora team! This guide will help you get started with the project.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone git@github.com:Bhagyashrikhamkar06/Skillora.git
cd Skillora
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 4. Set Up Database

```bash
# Create PostgreSQL database
createdb job_portal

# Run schema
psql job_portal < ../database/schema.sql
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory with the following:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/job_portal
MONGO_URI=mongodb://localhost:27017/job_portal

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Server
FLASK_ENV=development
FLASK_DEBUG=1
```

### 6. Run the Application

```bash
# Start backend
cd backend
python app.py

# Start frontend (in another terminal)
cd frontend
python -m http.server 8000
```

## 🔄 Git Workflow

### Branch Naming Convention

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes
- `docs/documentation-update` - Documentation updates

### Workflow Steps

1. **Pull latest changes**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes and commit**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub

### Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: add job recommendation algorithm
fix: resolve resume parsing error
docs: update API documentation
```

## 📁 Project Structure

```
Skillora/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models/                # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic
│   └── utils/                 # Helper functions
├── frontend/
│   ├── index.html             # Main page
│   ├── styles/                # CSS files
│   └── scripts/               # JavaScript files
├── database/
│   └── schema.sql             # Database schema
└── uploads/                   # User uploaded files
```

## 🧪 Testing

```bash
# Run tests
cd backend
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## 📝 Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features
- **CSS**: Use BEM naming convention
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

## 🐛 Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

## 💡 Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists
- Provide a clear use case
- Explain the expected behavior
- Consider implementation complexity

## 🤝 Code Review Process

1. All code must be reviewed before merging
2. Address all review comments
3. Ensure tests pass
4. Update documentation if needed
5. Squash commits before merging

## 📞 Communication

- Use GitHub Issues for bug reports and feature requests
- Use Pull Request comments for code discussions
- Tag team members when you need their input

## ⚠️ Important Notes

- Never commit `.env` files or sensitive credentials
- Always test your changes locally before pushing
- Keep your branch up to date with main
- Write meaningful commit messages
- Document your code

## 🎯 Development Tips

1. **Use virtual environment** to avoid dependency conflicts
2. **Test API endpoints** using Postman or curl
3. **Check browser console** for frontend errors
4. **Use git stash** to temporarily save uncommitted changes
5. **Pull before push** to avoid merge conflicts

## 📚 Useful Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [spaCy Documentation](https://spacy.io/usage)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

Happy coding! 🚀
