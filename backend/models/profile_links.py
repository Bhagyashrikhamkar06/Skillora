"""
Profile Links Model - Store and cache social profile data
"""
from models import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class ProfileLinks(db.Model):
    """Store user's social profile links and analysis"""
    __tablename__ = 'profile_links'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Profile URLs/Usernames
    github_username = db.Column(db.String(100))
    leetcode_username = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    
    # Cached profile data (JSON)
    github_data = db.Column(JSON)
    leetcode_data = db.Column(JSON)
    
    # Analysis scores
    github_score = db.Column(db.Integer, default=0)
    leetcode_score = db.Column(db.Integer, default=0)
    overall_score = db.Column(db.Integer, default=0)
    
    # AI-generated recommendations (JSON array)
    recommendations = db.Column(JSON)
    
    # Timestamps
    last_analyzed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('profile_links', uselist=False))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'github_username': self.github_username,
            'leetcode_username': self.leetcode_username,
            'linkedin_url': self.linkedin_url,
            'portfolio_url': self.portfolio_url,
            'github_score': self.github_score,
            'leetcode_score': self.leetcode_score,
            'overall_score': self.overall_score,
            'github_data': self.github_data,
            'leetcode_data': self.leetcode_data,
            'recommendations': self.recommendations,
            'last_analyzed_at': self.last_analyzed_at.isoformat() if self.last_analyzed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
