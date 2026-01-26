"""
Job routes for posting, searching, and managing jobs
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db
from models.job import Job
from models.user import User
from models.application import Application, SavedJob

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job posting (recruiter only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'recruiter':
            return jsonify({'error': 'Only recruiters can post jobs'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ('title', 'company_name', 'description', 'required_skills')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create job
        job = Job(
            recruiter_id=user_id,
            title=data['title'],
            company_name=data['company_name'],
            description=data['description'],
            required_skills=data['required_skills'],
            experience_min=data.get('experience_min'),
            experience_max=data.get('experience_max'),
            location=data.get('location'),
            job_type=data.get('job_type', 'Full-time'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            status='active'
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'message': 'Job created successfully',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/', methods=['GET'])
def get_jobs():
    """Get all jobs with pagination and filters"""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filters
        location = request.args.get('location')
        job_type = request.args.get('job_type')
        skills = request.args.get('skills')  # Comma-separated
        experience_min = request.args.get('experience_min', type=int)
        search = request.args.get('search')  # Search in title/company
        
        # Build query
        query = Job.query.filter_by(status='active')
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        if job_type:
            query = query.filter_by(job_type=job_type)
        
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            # Filter jobs that have any of the required skills
            query = query.filter(Job.required_skills.overlap(skill_list))
        
        if experience_min is not None:
            query = query.filter(Job.experience_min <= experience_min)
        
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Job.title.ilike(search_pattern),
                    Job.company_name.ilike(search_pattern)
                )
            )
        
        # Order by posted date (newest first)
        query = query.order_by(Job.posted_date.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        jobs = [job.to_dict(include_description=False) for job in pagination.items]
        
        return jsonify({
            'jobs': jobs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    try:
        job = Job.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Increment view count
        job.view_count += 1
        db.session.commit()
        
        return jsonify({'job': job.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update job (recruiter only, own jobs only)"""
    try:
        user_id = get_jwt_identity()
        job = Job.query.filter_by(id=job_id, recruiter_id=user_id).first()
        
        if not job:
            return jsonify({'error': 'Job not found or unauthorized'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            job.title = data['title']
        if 'description' in data:
            job.description = data['description']
        if 'required_skills' in data:
            job.required_skills = data['required_skills']
        if 'experience_min' in data:
            job.experience_min = data['experience_min']
        if 'experience_max' in data:
            job.experience_max = data['experience_max']
        if 'location' in data:
            job.location = data['location']
        if 'job_type' in data:
            job.job_type = data['job_type']
        if 'salary_min' in data:
            job.salary_min = data['salary_min']
        if 'salary_max' in data:
            job.salary_max = data['salary_max']
        if 'status' in data:
            job.status = data['status']
        if 'deadline' in data:
            job.deadline = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """Delete job (recruiter only, own jobs only)"""
    try:
        user_id = get_jwt_identity()
        job = Job.query.filter_by(id=job_id, recruiter_id=user_id).first()
        
        if not job:
            return jsonify({'error': 'Job not found or unauthorized'}), 404
        
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({'message': 'Job deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_job(job_id):
    """Apply to a job"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'job_seeker':
            return jsonify({'error': 'Only job seekers can apply to jobs'}), 403
        
        job = Job.query.get(job_id)
        
        if not job or job.status != 'active':
            return jsonify({'error': 'Job not found or not active'}), 404
        
        # Check if already applied
        existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
        if existing:
            return jsonify({'error': 'Already applied to this job'}), 409
        
        data = request.get_json() or {}
        
        # Create application
        application = Application(
            user_id=user_id,
            job_id=job_id,
            resume_id=data.get('resume_id'),
            cover_letter=data.get('cover_letter'),
            status='pending'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/<int:job_id>/save', methods=['POST'])
@jwt_required()
def save_job(job_id):
    """Save a job for later"""
    try:
        user_id = get_jwt_identity()
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if already saved
        existing = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
        if existing:
            return jsonify({'error': 'Job already saved'}), 409
        
        saved_job = SavedJob(user_id=user_id, job_id=job_id)
        db.session.add(saved_job)
        db.session.commit()
        
        return jsonify({'message': 'Job saved successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/saved', methods=['GET'])
@jwt_required()
def get_saved_jobs():
    """Get user's saved jobs"""
    try:
        user_id = get_jwt_identity()
        
        saved_jobs = SavedJob.query.filter_by(user_id=user_id).all()
        job_ids = [sj.job_id for sj in saved_jobs]
        
        jobs = Job.query.filter(Job.id.in_(job_ids)).all()
        
        return jsonify({
            'jobs': [job.to_dict(include_description=False) for job in jobs],
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/my-applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    """Get user's job applications"""
    try:
        user_id = get_jwt_identity()
        
        applications = Application.query.filter_by(user_id=user_id).order_by(Application.applied_date.desc()).all()
        
        result = []
        for app in applications:
            app_data = app.to_dict()
            app_data['job'] = app.job.to_dict(include_description=False)
            result.append(app_data)
        
        return jsonify({
            'applications': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
