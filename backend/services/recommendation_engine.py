"""
Intelligent job recommendation engine using TF-IDF and cosine similarity
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from models.job import Job
from models.resume import Resume, Skill


class RecommendationEngine:
    """Intelligent job matching and recommendation system"""
    
    def __init__(self):
        self.skill_weight = 0.5
        self.experience_weight = 0.25
        self.freshness_weight = 0.15
        self.location_weight = 0.1
        self.threshold = 0.6  # 60% minimum match
    
    def get_user_skills(self, user_id):
        """Get user's skills from active resume"""
        resume = Resume.query.filter_by(user_id=user_id, is_active=True).first()
        
        if not resume:
            return []
        
        skills = Skill.query.filter_by(resume_id=resume.id).all()
        return [skill.skill_name for skill in skills]
    
    def get_user_experience(self, user_id):
        """Get user's total experience in months"""
        resume = Resume.query.filter_by(user_id=user_id, is_active=True).first()
        
        if not resume:
            return 0
        
        return resume.total_experience_months or 0
    
    def get_user_location(self, user_id):
        """Get user's location"""
        from models.user import User
        user = User.query.get(user_id)
        return user.location if user else None
    
    def calculate_skill_match(self, user_skills, job_skills):
        """
        Calculate skill match using TF-IDF and cosine similarity
        Returns: similarity score (0-1)
        """
        if not user_skills or not job_skills:
            return 0.0
        
        # Prepare documents
        user_skills_text = ' '.join(user_skills)
        job_skills_text = ' '.join(job_skills)
        
        documents = [user_skills_text, job_skills_text]
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return similarity
    
    def calculate_experience_match(self, user_experience_months, job_exp_min, job_exp_max):
        """
        Calculate experience match score
        Returns: score (0-1)
        """
        if job_exp_min is None and job_exp_max is None:
            return 1.0  # No experience requirement
        
        user_experience_years = user_experience_months / 12.0
        
        # If only minimum is specified
        if job_exp_max is None:
            if user_experience_years >= job_exp_min:
                return 1.0
            else:
                return user_experience_years / job_exp_min if job_exp_min > 0 else 0.0
        
        # If only maximum is specified
        if job_exp_min is None:
            if user_experience_years <= job_exp_max:
                return 1.0
            else:
                return job_exp_max / user_experience_years if user_experience_years > 0 else 0.0
        
        # Both min and max specified
        if job_exp_min <= user_experience_years <= job_exp_max:
            return 1.0
        elif user_experience_years < job_exp_min:
            return user_experience_years / job_exp_min if job_exp_min > 0 else 0.0
        else:  # user_experience_years > job_exp_max
            # Penalize overqualification less
            return max(0.7, job_exp_max / user_experience_years) if user_experience_years > 0 else 0.0
    
    def calculate_freshness_score(self, posted_date):
        """
        Calculate job freshness score (newer jobs score higher)
        Returns: score (0-1)
        """
        if not posted_date:
            return 0.5
        
        days_old = (datetime.utcnow() - posted_date).days
        
        # Jobs posted in last 7 days get full score
        if days_old <= 7:
            return 1.0
        # Jobs posted in last 30 days get decreasing score
        elif days_old <= 30:
            return 1.0 - ((days_old - 7) / 23.0) * 0.5
        # Older jobs get lower score
        else:
            return max(0.1, 0.5 - ((days_old - 30) / 60.0) * 0.4)
    
    def calculate_location_match(self, user_location, job_location):
        """
        Calculate location match score
        Returns: score (0-1)
        """
        if not job_location:
            return 1.0  # Remote or location not specified
        
        if not user_location:
            return 0.5  # User location not specified
        
        # Simple string matching (can be enhanced with geolocation)
        user_loc_lower = user_location.lower()
        job_loc_lower = job_location.lower()
        
        if user_loc_lower == job_loc_lower:
            return 1.0
        elif user_loc_lower in job_loc_lower or job_loc_lower in user_loc_lower:
            return 0.8
        else:
            return 0.3
    
    def calculate_weighted_score(self, skill_score, exp_score, freshness_score, location_score):
        """
        Calculate weighted final score
        Returns: weighted score (0-1)
        """
        weighted_score = (
            skill_score * self.skill_weight +
            exp_score * self.experience_weight +
            freshness_score * self.freshness_weight +
            location_score * self.location_weight
        )
        
        return weighted_score
    
    def explain_recommendation(self, job, skill_score, exp_score, freshness_score, location_score, final_score):
        """
        Generate explanation for why job was recommended
        Returns: explanation dict
        """
        explanation = {
            'final_score': round(final_score * 100, 2),
            'breakdown': {
                'skill_match': {
                    'score': round(skill_score * 100, 2),
                    'weight': self.skill_weight * 100,
                    'contribution': round(skill_score * self.skill_weight * 100, 2)
                },
                'experience_match': {
                    'score': round(exp_score * 100, 2),
                    'weight': self.experience_weight * 100,
                    'contribution': round(exp_score * self.experience_weight * 100, 2)
                },
                'job_freshness': {
                    'score': round(freshness_score * 100, 2),
                    'weight': self.freshness_weight * 100,
                    'contribution': round(freshness_score * self.freshness_weight * 100, 2)
                },
                'location_match': {
                    'score': round(location_score * 100, 2),
                    'weight': self.location_weight * 100,
                    'contribution': round(location_score * self.location_weight * 100, 2)
                }
            }
        }
        
        return explanation
    
    def recommend_jobs(self, user_id, limit=20):
        """
        Get personalized job recommendations for user
        Returns: list of (job, score, explanation) tuples
        """
        # Get user data
        user_skills = self.get_user_skills(user_id)
        user_experience = self.get_user_experience(user_id)
        user_location = self.get_user_location(user_id)
        
        if not user_skills:
            return []
        
        # Get active jobs
        jobs = Job.query.filter_by(status='active').all()
        
        recommendations = []
        
        for job in jobs:
            # Calculate individual scores
            skill_score = self.calculate_skill_match(user_skills, job.required_skills or [])
            exp_score = self.calculate_experience_match(user_experience, job.experience_min, job.experience_max)
            freshness_score = self.calculate_freshness_score(job.posted_date)
            location_score = self.calculate_location_match(user_location, job.location)
            
            # Calculate weighted final score
            final_score = self.calculate_weighted_score(skill_score, exp_score, freshness_score, location_score)
            
            # Only recommend if above threshold
            if final_score >= self.threshold:
                explanation = self.explain_recommendation(
                    job, skill_score, exp_score, freshness_score, location_score, final_score
                )
                
                recommendations.append({
                    'job': job,
                    'score': final_score,
                    'explanation': explanation
                })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N recommendations
        return recommendations[:limit]
