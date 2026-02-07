"""
Job model for job postings
"""
from datetime import datetime
from models import db


class Job(db.Model):
    """Job posting model"""
    
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    description = db.Column(db.Text)
    required_skills = db.Column(db.JSON)  # Array of skills
    experience_min = db.Column(db.Integer)
    experience_max = db.Column(db.Integer)
    location = db.Column(db.String(255))
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, Remote
    salary_min = db.Column(db.Numeric(10, 2))
    salary_max = db.Column(db.Numeric(10, 2))
    posted_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active', index=True)  # active, closed, filled
    source = db.Column(db.String(50), default='internal')  # internal, scraped, api
    external_url = db.Column(db.Text)
    view_count = db.Column(db.Integer, default=0)
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    saved_by = db.relationship('SavedJob', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_description=True):
        """Convert job to dictionary"""
        data = {
            'id': self.id,
            'recruiter_id': self.recruiter_id,
            'title': self.title,
            'company_name': self.company_name,
            'required_skills': self.required_skills,
            'experience_min': self.experience_min,
            'experience_max': self.experience_max,
            'location': self.location,
            'job_type': self.job_type,
            'salary_min': float(self.salary_min) if self.salary_min else None,
            'salary_max': float(self.salary_max) if self.salary_max else None,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'source': self.source,
            'external_url': self.external_url,
            'view_count': self.view_count
        }
        
        if include_description:
            data['description'] = self.description
        
        return data
    
    def __repr__(self):
        return f'<Job {self.id} - {self.title}>'
