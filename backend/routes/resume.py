"""
Resume routes for upload and management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db
from models.resume import Resume, Skill
from models.user import User

# Try to import the full parser, fall back to simple one if spaCy not available
try:
    from services.resume_parser import ResumeParser
except ImportError:
    from services.resume_parser_simple import ResumeParser
    
from utils.file_handler import save_uploaded_file, delete_file

resume_bp = Blueprint('resume', __name__)
parser = None

def get_parser():
    global parser
    if parser is None:
        parser = ResumeParser()
    return parser


@resume_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload and parse resume"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file
        file_path, file_name, file_size = save_uploaded_file(file, user_id)
        
        # Parse resume
        try:
            parsed_data, ats_score = get_parser().parse_resume(file_path)
        except Exception as e:
            # Delete file if parsing fails
            delete_file(file_path)
            return jsonify({'error': f'Error parsing resume: {str(e)}'}), 500
        
        # Deactivate previous resumes
        Resume.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
        
        # Create resume record
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            parsed_data=parsed_data,
            total_experience_months=parsed_data.get('total_experience_months', 0),
            quality_score=ats_score,
            is_active=True
        )
        
        db.session.add(resume)
        db.session.flush()  # Get resume ID
        
        # Add skills
        skills_data = parsed_data.get('skills', {})
        categorized_skills = skills_data.get('categorized', {})
        
        for skill_name, category in categorized_skills.items():
            skill = Skill(
                resume_id=resume.id,
                skill_name=skill_name,
                skill_category=category
            )
            db.session.add(skill)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded and parsed successfully',
            'resume': resume.to_dict(),
            'ats_score': float(ats_score),
            'skills_found': len(skills_data.get('all_skills', []))
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """Get resume details"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Get skills
        skills = Skill.query.filter_by(resume_id=resume_id).all()
        
        resume_data = resume.to_dict()
        resume_data['skills'] = [skill.to_dict() for skill in skills]
        
        return jsonify({'resume': resume_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_resume():
    """Get user's active resume"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.filter_by(user_id=user_id, is_active=True).first()
        
        if not resume:
            return jsonify({'error': 'No active resume found'}), 404
        
        # Get skills
        skills = Skill.query.filter_by(resume_id=resume.id).all()
        
        resume_data = resume.to_dict()
        resume_data['skills'] = [skill.to_dict() for skill in skills]
        
        return jsonify({'resume': resume_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_resumes():
    """Get all user's resumes"""
    try:
        user_id = int(get_jwt_identity())
        resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.upload_date.desc()).all()
        
        return jsonify({
            'resumes': [resume.to_dict() for resume in resumes],
            'count': len(resumes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """Delete resume"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Delete file
        delete_file(resume.file_path)
        
        # Delete from database (skills will be deleted automatically due to cascade)
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({'message': 'Resume deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/<int:resume_id>/activate', methods=['PUT'])
@jwt_required()
def activate_resume(resume_id):
    """Set resume as active"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Deactivate all other resumes
        Resume.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
        
        # Activate this resume
        resume.is_active = True
        db.session.commit()
        
        return jsonify({'message': 'Resume activated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
