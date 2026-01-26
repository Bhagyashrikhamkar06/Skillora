"""
Main Flask application
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env file FIRST

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from models import db

# Import models to register them
from models.user import User
from models.resume import Resume, Skill
from models.job import Job
from models.application import Application, SavedJob
from models.interview import InterviewSession, InterviewQA
from models.profile_links import ProfileLinks


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.resume import resume_bp
    from routes.jobs import jobs_bp
    from routes.recommendations import recommendations_bp
    from routes.interview import interview_bp
    from routes.profile_analysis import profile_analysis_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(profile_analysis_bp, url_prefix='/api/profile-analysis')
    
    # Tables already created via schema.sql - no need for create_all()
    # with app.app_context():
    #     db.create_all()
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'API is running'})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
