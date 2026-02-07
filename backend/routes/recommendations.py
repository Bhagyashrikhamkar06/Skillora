"""
Recommendation routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.recommendation_engine import RecommendationEngine

recommendations_bp = Blueprint('recommendations', __name__)
engine = None

def get_engine():
    global engine
    if engine is None:
        engine = RecommendationEngine()
    return engine


@recommendations_bp.route('/', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized job recommendations"""
    try:
        user_id = get_jwt_identity()
        
        # Get limit from query params
        limit = request.args.get('limit', 20, type=int)
        
        # Get recommendations
        recommendations = get_engine().recommend_jobs(user_id, limit=limit)
        
        if not recommendations:
            return jsonify({
                'message': 'No recommendations found. Please upload a resume first.',
                'recommendations': [],
                'count': 0
            }), 200
        
        # Format response
        result = []
        for rec in recommendations:
            result.append({
                'job': rec['job'].to_dict(include_description=False),
                'match_score': round(rec['score'] * 100, 2),
                'explanation': rec['explanation']
            })
        
        return jsonify({
            'recommendations': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendations_bp.route('/similar/<int:job_id>', methods=['GET'])
def get_similar_jobs(job_id):
    """Get jobs similar to a specific job"""
    try:
        from models.job import Job
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Get the reference job
        reference_job = Job.query.get(job_id)
        
        if not reference_job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get all active jobs except the reference
        all_jobs = Job.query.filter(Job.id != job_id, Job.status == 'active').all()
        
        if not all_jobs:
            return jsonify({'similar_jobs': [], 'count': 0}), 200
        
        # Prepare job descriptions for comparison
        ref_skills = ' '.join(reference_job.required_skills or [])
        ref_text = f"{reference_job.title} {reference_job.description} {ref_skills}"
        
        job_texts = [ref_text]
        job_objects = [reference_job]
        
        for job in all_jobs:
            skills = ' '.join(job.required_skills or [])
            text = f"{job.title} {job.description} {skills}"
            job_texts.append(text)
            job_objects.append(job)
        
        # Calculate TF-IDF and similarity
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf_matrix = vectorizer.fit_transform(job_texts)
        
        # Calculate similarity with reference job
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Create list of (job, similarity) tuples
        similar_jobs = [(job_objects[i+1], similarities[i]) for i in range(len(similarities))]
        
        # Sort by similarity
        similar_jobs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 10
        result = []
        for job, similarity in similar_jobs[:10]:
            result.append({
                'job': job.to_dict(include_description=False),
                'similarity_score': round(similarity * 100, 2)
            })
        
        return jsonify({
            'similar_jobs': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
