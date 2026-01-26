"""
Resume model for storing parsed resume data
"""
from datetime import datetime
from models import db


class Resume(db.Model):
    """Resume model for storing uploaded and parsed resumes"""
    
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.Text)
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    parsed_data = db.Column(db.JSON)  # Structured resume data
    total_experience_months = db.Column(db.Integer)
    quality_score = db.Column(db.Numeric(3, 2))  # ATS score 0-10
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    skills = db.relationship('Skill', backref='resume', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='resume', lazy=True)
    
    def to_dict(self):
        """Convert resume to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'parsed_data': self.parsed_data,
            'total_experience_months': self.total_experience_months,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Resume {self.id} - {self.file_name}>'


class Skill(db.Model):
    """Skills extracted from resumes"""
    
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    skill_name = db.Column(db.String(100))
    skill_category = db.Column(db.String(50))  # Programming, Database, Cloud, etc.
    proficiency_level = db.Column(db.String(20))  # Beginner, Intermediate, Expert
    years_of_experience = db.Column(db.Numeric(3, 1))
    
    def to_dict(self):
        """Convert skill to dictionary"""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'skill_category': self.skill_category,
            'proficiency_level': self.proficiency_level,
            'years_of_experience': float(self.years_of_experience) if self.years_of_experience else None
        }
    
    def __repr__(self):
        return f'<Skill {self.skill_name}>'
