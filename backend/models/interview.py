"""
Interview session models
"""
from datetime import datetime
from models import db


class InterviewSession(db.Model):
    """Mock interview session model"""
    
    __tablename__ = 'interview_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_role = db.Column(db.String(255))
    interview_type = db.Column(db.String(50))  # HR, Technical, Behavioral
    difficulty_level = db.Column(db.String(20))  # Easy, Medium, Hard
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_questions = db.Column(db.Integer)
    overall_score = db.Column(db.Numeric(4, 2))
    performance_level = db.Column(db.String(20))  # Beginner, Intermediate, Job-Ready
    feedback_summary = db.Column(db.Text)
    
    # Relationships
    questions = db.relationship('InterviewQA', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert interview session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_role': self.job_role,
            'interview_type': self.interview_type,
            'difficulty_level': self.difficulty_level,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_questions': self.total_questions,
            'overall_score': float(self.overall_score) if self.overall_score else None,
            'performance_level': self.performance_level,
            'feedback_summary': self.feedback_summary
        }
    
    def __repr__(self):
        return f'<InterviewSession {self.id} - {self.job_role}>'


class InterviewQA(db.Model):
    """Interview questions and answers"""
    
    __tablename__ = 'interview_qa'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    question_number = db.Column(db.Integer)
    question = db.Column(db.Text)
    user_answer = db.Column(db.Text)
    model_answer = db.Column(db.Text)
    score = db.Column(db.Numeric(3, 1))  # 0-10
    technical_correctness = db.Column(db.Numeric(3, 1))
    clarity_score = db.Column(db.Numeric(3, 1))
    relevance_score = db.Column(db.Numeric(3, 1))
    feedback = db.Column(db.Text)
    strengths = db.Column(db.Text)
    improvements = db.Column(db.Text)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert QA to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_number': self.question_number,
            'question': self.question,
            'user_answer': self.user_answer,
            'model_answer': self.model_answer,
            'score': float(self.score) if self.score else None,
            'technical_correctness': float(self.technical_correctness) if self.technical_correctness else None,
            'clarity_score': float(self.clarity_score) if self.clarity_score else None,
            'relevance_score': float(self.relevance_score) if self.relevance_score else None,
            'feedback': self.feedback,
            'strengths': self.strengths,
            'improvements': self.improvements,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }
    
    def __repr__(self):
        return f'<InterviewQA {self.id} - Q{self.question_number}>'
