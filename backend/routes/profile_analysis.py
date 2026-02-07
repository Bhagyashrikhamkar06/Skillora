"""
Profile Analysis Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db
from models.user import User
from models.profile_links import ProfileLinks
from services.profile_scraper import ProfileScraper
from services.profile_analyzer import ProfileAnalyzer

profile_analysis_bp = Blueprint('profile_analysis', __name__)

scraper = None
analyzer = None

def get_scraper():
    global scraper
    if scraper is None:
        scraper = ProfileScraper()
    return scraper

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = ProfileAnalyzer()
    return analyzer


@profile_analysis_bp.route('/extract', methods=['POST'])
@jwt_required()
def extract_profile_links():
    """
    Extract profile links from resume text
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            return jsonify({'error': 'Resume text is required'}), 400
        
        # Extract links
        links = get_scraper().extract_profile_links(resume_text)
        
        # Get or create profile_links record
        profile_links = ProfileLinks.query.filter_by(user_id=user_id).first()
        if not profile_links:
            profile_links = ProfileLinks(user_id=user_id)
            db.session.add(profile_links)
        
        # Update links
        if links.get('github'):
            profile_links.github_username = links['github']
        if links.get('leetcode'):
            profile_links.leetcode_username = links['leetcode']
        if links.get('linkedin'):
            profile_links.linkedin_url = links['linkedin']
        if links.get('portfolio'):
            profile_links.portfolio_url = links['portfolio']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile links extracted successfully',
            'links': links,
            'profile': profile_links.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@profile_analysis_bp.route('/scrape', methods=['POST'])
@jwt_required()
def scrape_and_analyze():
    """
    Scrape social profiles and perform analysis
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Get profile links
        profile_links = ProfileLinks.query.filter_by(user_id=user_id).first()
        if not profile_links:
            return jsonify({'error': 'No profile links found. Please add your profiles first.'}), 404
        
        # Check if we need to re-scrape (cache for 24 hours)
        if profile_links.last_analyzed_at:
            time_since_analysis = datetime.utcnow() - profile_links.last_analyzed_at
            if time_since_analysis < timedelta(hours=24):
                return jsonify({
                    'message': 'Using cached analysis',
                    'profile': profile_links.to_dict(),
                    'cached': True
                }), 200
        
        # Scrape GitHub
        github_data = {}
        github_analysis = {'score': 0}
        if profile_links.github_username:
            github_data = get_scraper().scrape_github_profile(profile_links.github_username)
            github_analysis = get_analyzer().analyze_github_profile(github_data)
            profile_links.github_data = github_data
            profile_links.github_score = github_analysis.get('score', 0)
        
        # Scrape LeetCode
        leetcode_data = {}
        leetcode_analysis = {'score': 0}
        if profile_links.leetcode_username:
            leetcode_data = get_scraper().scrape_leetcode_profile(profile_links.leetcode_username)
            leetcode_analysis = get_analyzer().analyze_leetcode_profile(leetcode_data)
            profile_links.leetcode_data = leetcode_data
            profile_links.leetcode_score = leetcode_analysis.get('score', 0)
        
        # Calculate overall score
        overall_score = get_analyzer().calculate_overall_score(github_analysis, leetcode_analysis)
        profile_links.overall_score = overall_score
        
        # Generate AI recommendations
        recommendations = get_analyzer().generate_improvement_recommendations(
            github_data, 
            leetcode_data
        )
        profile_links.recommendations = recommendations
        
        # Update timestamp
        profile_links.last_analyzed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile analysis completed successfully',
            'profile': profile_links.to_dict(),
            'github_analysis': github_analysis,
            'leetcode_analysis': leetcode_analysis,
            'overall_score': overall_score,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@profile_analysis_bp.route('/report', methods=['GET'])
@jwt_required()
def get_analysis_report():
    """
    Get comprehensive profile analysis report
    """
    try:
        user_id = int(get_jwt_identity())
        
        profile_links = ProfileLinks.query.filter_by(user_id=user_id).first()
        if not profile_links:
            return jsonify({'error': 'No profile analysis found'}), 404
        
        # Re-analyze if needed
        github_analysis = get_analyzer().analyze_github_profile(profile_links.github_data or {})
        leetcode_analysis = get_analyzer().analyze_leetcode_profile(profile_links.leetcode_data or {})
        
        return jsonify({
            'profile': profile_links.to_dict(),
            'github_analysis': github_analysis,
            'leetcode_analysis': leetcode_analysis,
            'overall_score': profile_links.overall_score,
            'recommendations': profile_links.recommendations or []
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_analysis_bp.route('/links', methods=['PUT'])
@jwt_required()
def update_profile_links():
    """
    Manually update profile links
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        profile_links = ProfileLinks.query.filter_by(user_id=user_id).first()
        if not profile_links:
            profile_links = ProfileLinks(user_id=user_id)
            db.session.add(profile_links)
        
        # Update links
        if 'github_username' in data:
            profile_links.github_username = data['github_username']
        if 'leetcode_username' in data:
            profile_links.leetcode_username = data['leetcode_username']
        if 'linkedin_url' in data:
            profile_links.linkedin_url = data['linkedin_url']
        if 'portfolio_url' in data:
            profile_links.portfolio_url = data['portfolio_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile links updated successfully',
            'profile': profile_links.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@profile_analysis_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_analysis():
    """
    Force refresh profile analysis (bypass cache)
    """
    try:
        user_id = int(get_jwt_identity())
        
        profile_links = ProfileLinks.query.filter_by(user_id=user_id).first()
        if not profile_links:
            return jsonify({'error': 'No profile links found'}), 404
        
        # Clear cache
        get_scraper().clear_cache()
        
        # Force re-scrape by setting last_analyzed_at to None
        profile_links.last_analyzed_at = None
        db.session.commit()
        
        # Call scrape_and_analyze
        return scrape_and_analyze()
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
