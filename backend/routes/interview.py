"""
Mock interview routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db
from models.interview import InterviewSession, InterviewQA
from models.user import User
from services.interview_ai import InterviewAI

interview_bp = Blueprint('interview', __name__)

# Initialize AI service (will be created when first used)
ai_service = None

def get_ai_service():
    """Lazy initialization of AI service"""
    global ai_service
    if ai_service is None:
        try:
            ai_service = InterviewAI()
        except Exception as e:
            raise Exception(f"Failed to initialize AI service: {str(e)}")
    return ai_service


@interview_bp.route('/start', methods=['POST'])
@jwt_required()
def start_interview():
    """Start a new mock interview session"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'job_seeker':
            return jsonify({'error': 'Only job seekers can start interviews'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ('job_role', 'interview_type')):
            return jsonify({'error': 'Missing required fields: job_role, interview_type'}), 400
        
        job_role = data['job_role']
        interview_type = data['interview_type']  # HR, Technical, Behavioral
        
        if interview_type not in ['HR', 'Technical', 'Behavioral']:
            return jsonify({'error': 'Invalid interview type'}), 400
        
        # Get user profile
        ai = get_ai_service()
        skills, experience_level = ai.get_user_profile(user_id)
        
        if not skills:
            return jsonify({'error': 'Please upload a resume first'}), 400
        
        # Create interview session
        session = InterviewSession(
            user_id=user_id,
            job_role=job_role,
            interview_type=interview_type,
            difficulty_level=experience_level,
            total_questions=0
        )
        
        db.session.add(session)
        db.session.flush()  # Get session ID
        
        # Generate first question
        question = ai.generate_question(
            job_role, skills, experience_level, interview_type, 1
        )
        
        # Store question
        qa = InterviewQA(
            session_id=session.id,
            question_number=1,
            question=question
        )
        
        db.session.add(qa)
        session.total_questions = 1
        db.session.commit()
        
        return jsonify({
            'message': 'Interview started successfully',
            'session_id': session.id,
            'question_number': 1,
            'question': question,
            'interview_type': interview_type,
            'job_role': job_role
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/answer', methods=['POST'])
@jwt_required()
def submit_answer():
    """Submit answer and get next question"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ('session_id', 'question_number', 'answer')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        session_id = data['session_id']
        question_number = data['question_number']
        user_answer = data['answer']
        
        # Get session
        session = InterviewSession.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get question
        qa = InterviewQA.query.filter_by(
            session_id=session_id,
            question_number=question_number
        ).first()
        
        if not qa:
            return jsonify({'error': 'Question not found'}), 404
        
        # Evaluate answer
        ai = get_ai_service()
        evaluation = ai.evaluate_answer(
            qa.question, user_answer, session.job_role, session.interview_type
        )
        
        # Update QA with answer and evaluation
        qa.user_answer = user_answer
        qa.score = evaluation['score']
        qa.technical_correctness = evaluation['technical_correctness']
        qa.clarity_score = evaluation['clarity_score']
        qa.relevance_score = evaluation['relevance_score']
        qa.feedback = evaluation['feedback']
        qa.strengths = evaluation['strengths']
        qa.improvements = evaluation['improvements']
        qa.model_answer = evaluation['model_answer']
        
        # Check if we should generate next question
        max_questions = 5  # Limit questions per session
        generate_next = question_number < max_questions
        
        next_question = None
        next_question_number = None
        
        if generate_next:
            # Get user profile
            skills, experience_level = ai.get_user_profile(user_id)
            
            # Generate next question
            next_question_number = question_number + 1
            next_question = ai.generate_question(
                session.job_role, skills, experience_level,
                session.interview_type, next_question_number
            )
            
            # Store next question
            next_qa = InterviewQA(
                session_id=session.id,
                question_number=next_question_number,
                question=next_question
            )
            
            db.session.add(next_qa)
            session.total_questions = next_question_number
        
        db.session.commit()
        
        response = {
            'message': 'Answer submitted successfully',
            'evaluation': {
                'score': float(evaluation['score']),
                'technical_correctness': float(evaluation['technical_correctness']),
                'clarity': float(evaluation['clarity_score']),
                'relevance': float(evaluation['relevance_score']),
                'strengths': evaluation['strengths'],
                'improvements': evaluation['improvements'],
                'model_answer': evaluation['model_answer']
            }
        }
        
        if generate_next:
            response['next_question'] = {
                'question_number': next_question_number,
                'question': next_question
            }
        else:
            response['interview_complete'] = True
            response['message'] = 'Interview complete! Call /complete to get final feedback.'
        
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/<int:session_id>/complete', methods=['POST'])
@jwt_required()
def complete_interview(session_id):
    """Complete interview and get final feedback"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get session
        session = InterviewSession.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if session.end_time:
            return jsonify({'error': 'Interview already completed'}), 400
        
        # Get all Q&A
        qa_list = InterviewQA.query.filter_by(session_id=session_id).order_by(InterviewQA.question_number).all()
        
        if not qa_list or not qa_list[0].user_answer:
            return jsonify({'error': 'No answers submitted yet'}), 400
        
        # Prepare data for final feedback
        qa_pairs = []
        total_score = 0
        answered_count = 0
        
        for qa in qa_list:
            if qa.user_answer:
                qa_pairs.append({
                    'question': qa.question,
                    'answer': qa.user_answer,
                    'score': float(qa.score) if qa.score else 0
                })
                total_score += float(qa.score) if qa.score else 0
                answered_count += 1
        
        if answered_count == 0:
            return jsonify({'error': 'No answers to evaluate'}), 400
        
        # Generate final feedback
        ai = get_ai_service()
        session_data = {
            'job_role': session.job_role,
            'interview_type': session.interview_type,
            'qa_pairs': qa_pairs
        }
        
        feedback, performance_level = ai.generate_final_feedback(session_data)
        
        # Update session
        session.end_time = datetime.utcnow()
        session.overall_score = total_score / answered_count
        session.performance_level = performance_level
        session.feedback_summary = feedback
        
        db.session.commit()
        
        return jsonify({
            'message': 'Interview completed successfully',
            'overall_score': round(float(session.overall_score), 2),
            'performance_level': performance_level,
            'feedback': feedback,
            'questions_answered': answered_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/<int:session_id>', methods=['GET'])
@jwt_required()
def get_interview_session(session_id):
    """Get interview session details"""
    try:
        user_id = int(get_jwt_identity())
        
        session = InterviewSession.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get all Q&A
        qa_list = InterviewQA.query.filter_by(session_id=session_id).order_by(InterviewQA.question_number).all()
        
        session_data = session.to_dict()
        session_data['questions'] = [qa.to_dict() for qa in qa_list]
        
        return jsonify({'session': session_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/history', methods=['GET'])
@jwt_required()
def get_interview_history():
    """Get user's interview history"""
    try:
        user_id = int(get_jwt_identity())
        
        sessions = InterviewSession.query.filter_by(user_id=user_id).order_by(InterviewSession.start_time.desc()).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
