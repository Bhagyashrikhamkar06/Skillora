"""
Application and SavedJob models
"""
from datetime import datetime
from models import db


class Application(db.Model):
    """Job application model"""
    
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'))
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, shortlisted, rejected, accepted
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    cover_letter = db.Column(db.Text)
    match_score = db.Column(db.Numeric(5, 2))  # Percentage match
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_user_job_application'),
    )
    
    def to_dict(self):
        """Convert application to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'resume_id': self.resume_id,
            'status': self.status,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'cover_letter': self.cover_letter,
            'match_score': float(self.match_score) if self.match_score else None
        }
    
    def __repr__(self):
        return f'<Application {self.id} - User:{self.user_id} Job:{self.job_id}>'


class SavedJob(db.Model):
    """Saved jobs model"""
    
    __tablename__ = 'saved_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    saved_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_user_saved_job'),
    )
    
    def to_dict(self):
        """Convert saved job to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'saved_date': self.saved_date.isoformat() if self.saved_date else None
        }
    
    def __repr__(self):
        return f'<SavedJob {self.id} - User:{self.user_id} Job:{self.job_id}>'
