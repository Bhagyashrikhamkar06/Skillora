"""
AI-powered mock interview service
"""
import os
import re
from openai import OpenAI
from prompts.interview_prompts import InterviewPrompts
from models.resume import Resume, Skill


class InterviewAI:
    """AI-powered interview system using LLM"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.prompts = InterviewPrompts()
    
    def get_user_profile(self, user_id):
        """Get user's skills and experience from resume"""
        resume = Resume.query.filter_by(user_id=user_id, is_active=True).first()
        
        if not resume:
            return None, None
        
        # Get skills
        skills = Skill.query.filter_by(resume_id=resume.id).all()
        skill_names = [skill.skill_name for skill in skills]
        
        # Determine experience level
        experience_months = resume.total_experience_months or 0
        if experience_months < 12:
            experience_level = 'Beginner'
        elif experience_months < 36:
            experience_level = 'Intermediate'
        else:
            experience_level = 'Expert'
        
        return skill_names, experience_level
    
    def generate_question(self, job_role, skills, experience_level, interview_type, question_number):
        """
        Generate interview question using LLM
        
        Returns: question text
        """
        prompt = self.prompts.generate_question_prompt(
            job_role, skills, experience_level, interview_type, question_number
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use gpt-4 for better quality
                messages=[
                    {"role": "system", "content": "You are an expert interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            question = response.choices[0].message.content.strip()
            return question
            
        except Exception as e:
            raise Exception(f"Error generating question: {str(e)}")
    
    def evaluate_answer(self, question, user_answer, job_role, interview_type):
        """
        Evaluate user's answer using LLM
        
        Returns: dict with scores and feedback
        """
        prompt = self.prompts.evaluate_answer_prompt(
            question, user_answer, job_role, interview_type
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interview evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            evaluation_text = response.choices[0].message.content.strip()
            
            # Parse the response
            evaluation = self._parse_evaluation(evaluation_text)
            
            return evaluation
            
        except Exception as e:
            raise Exception(f"Error evaluating answer: {str(e)}")
    
    def _parse_evaluation(self, evaluation_text):
        """Parse LLM evaluation response into structured format"""
        try:
            # Extract scores
            score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', evaluation_text)
            technical_match = re.search(r'TECHNICAL:\s*(\d+(?:\.\d+)?)', evaluation_text)
            clarity_match = re.search(r'CLARITY:\s*(\d+(?:\.\d+)?)', evaluation_text)
            relevance_match = re.search(r'RELEVANCE:\s*(\d+(?:\.\d+)?)', evaluation_text)
            
            # Extract strengths
            strengths_section = re.search(r'STRENGTHS:(.*?)(?=IMPROVEMENTS:|$)', evaluation_text, re.DOTALL)
            strengths = []
            if strengths_section:
                strengths = [s.strip('- ').strip() for s in strengths_section.group(1).split('\n') if s.strip().startswith('-')]
            
            # Extract improvements
            improvements_section = re.search(r'IMPROVEMENTS:(.*?)(?=MODEL_ANSWER:|$)', evaluation_text, re.DOTALL)
            improvements = []
            if improvements_section:
                improvements = [s.strip('- ').strip() for s in improvements_section.group(1).split('\n') if s.strip().startswith('-')]
            
            # Extract model answer
            model_answer_match = re.search(r'MODEL_ANSWER:(.*?)$', evaluation_text, re.DOTALL)
            model_answer = model_answer_match.group(1).strip() if model_answer_match else ""
            
            return {
                'score': float(score_match.group(1)) if score_match else 5.0,
                'technical_correctness': float(technical_match.group(1)) if technical_match else 5.0,
                'clarity_score': float(clarity_match.group(1)) if clarity_match else 5.0,
                'relevance_score': float(relevance_match.group(1)) if relevance_match else 5.0,
                'strengths': '\n'.join(strengths) if strengths else "Good effort",
                'improvements': '\n'.join(improvements) if improvements else "Keep practicing",
                'model_answer': model_answer,
                'feedback': evaluation_text
            }
            
        except Exception as e:
            # Fallback if parsing fails
            return {
                'score': 5.0,
                'technical_correctness': 5.0,
                'clarity_score': 5.0,
                'relevance_score': 5.0,
                'strengths': "Answer provided",
                'improvements': "Continue practicing",
                'model_answer': "",
                'feedback': evaluation_text
            }
    
    def generate_final_feedback(self, session_data):
        """
        Generate final interview feedback
        
        Args:
            session_data: Dict with job_role, interview_type, qa_pairs
        
        Returns: feedback text
        """
        prompt = self.prompts.final_feedback_prompt(session_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            feedback = response.choices[0].message.content.strip()
            
            # Determine performance level from feedback
            if "Job-Ready" in feedback:
                performance_level = "Job-Ready"
            elif "Intermediate" in feedback:
                performance_level = "Intermediate"
            else:
                performance_level = "Beginner"
            
            return feedback, performance_level
            
        except Exception as e:
            raise Exception(f"Error generating final feedback: {str(e)}")
