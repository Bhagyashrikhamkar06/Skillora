"""
Interview prompts for AI mock interview system
"""


class InterviewPrompts:
    """Structured prompts for AI interview system"""
    
    @staticmethod
    def generate_question_prompt(job_role, skills, experience_level, interview_type, question_number):
        """
        Generate prompt for creating interview questions
        
        Args:
            job_role: Target job role
            skills: List of candidate skills
            experience_level: Beginner/Intermediate/Expert
            interview_type: HR/Technical/Behavioral
            question_number: Current question number
        """
        skills_str = ', '.join(skills[:10])  # Limit to top 10 skills
        
        if interview_type == 'HR':
            prompt = f"""You are an experienced HR interviewer conducting an interview for a {job_role} position.

Candidate Profile:
- Role: {job_role}
- Experience Level: {experience_level}
- Key Skills: {skills_str}

This is question #{question_number} in the HR round.

Generate ONE professional HR interview question. The question should:
1. Be appropriate for the experience level
2. Help assess cultural fit and soft skills
3. Be clear and concise
4. Not be too generic

Return ONLY the question, nothing else."""

        elif interview_type == 'Technical':
            prompt = f"""You are an experienced technical interviewer for a {job_role} position.

Candidate Profile:
- Role: {job_role}
- Experience Level: {experience_level}
- Technical Skills: {skills_str}

This is question #{question_number} in the technical round.

Generate ONE technical interview question based on the candidate's skills. The question should:
1. Test practical knowledge of their listed skills
2. Be appropriate for {experience_level} level
3. Have a clear, specific answer
4. Not be too theoretical

Return ONLY the question, nothing else."""

        else:  # Behavioral
            prompt = f"""You are an experienced interviewer conducting a behavioral interview for a {job_role} position.

Candidate Profile:
- Role: {job_role}
- Experience Level: {experience_level}

This is question #{question_number} in the behavioral round.

Generate ONE behavioral interview question using the STAR method (Situation, Task, Action, Result). The question should:
1. Ask about past experiences
2. Be relevant to the role
3. Help assess problem-solving and teamwork
4. Start with phrases like "Tell me about a time when..." or "Describe a situation where..."

Return ONLY the question, nothing else."""
        
        return prompt
    
    @staticmethod
    def evaluate_answer_prompt(question, user_answer, job_role, interview_type):
        """
        Generate prompt for evaluating candidate's answer
        
        Args:
            question: The interview question
            user_answer: Candidate's answer
            job_role: Target job role
            interview_type: HR/Technical/Behavioral
        """
        prompt = f"""You are an expert interview evaluator for a {job_role} position.

Interview Type: {interview_type}
Question: {question}

Candidate's Answer:
{user_answer}

Evaluate this answer and provide:

1. **Score** (0-10): Overall quality of the answer
2. **Technical Correctness** (0-10): How accurate is the answer (for technical questions)
3. **Clarity** (0-10): How clear and well-structured is the answer
4. **Relevance** (0-10): How relevant is the answer to the question

5. **Strengths**: What the candidate did well (2-3 bullet points)
6. **Areas for Improvement**: What could be better (2-3 bullet points)
7. **Model Answer**: A brief example of a strong answer to this question

Format your response EXACTLY as follows:
SCORE: [number]
TECHNICAL: [number]
CLARITY: [number]
RELEVANCE: [number]
STRENGTHS:
- [strength 1]
- [strength 2]
IMPROVEMENTS:
- [improvement 1]
- [improvement 2]
MODEL_ANSWER:
[your model answer here]"""
        
        return prompt
    
    @staticmethod
    def final_feedback_prompt(session_data):
        """
        Generate prompt for final interview feedback
        
        Args:
            session_data: Dict with job_role, questions, answers, scores
        """
        qa_summary = "\n\n".join([
            f"Q{i+1}: {qa['question']}\nAnswer: {qa['answer']}\nScore: {qa['score']}/10"
            for i, qa in enumerate(session_data['qa_pairs'])
        ])
        
        avg_score = sum(qa['score'] for qa in session_data['qa_pairs']) / len(session_data['qa_pairs'])
        
        prompt = f"""You are an expert career coach providing final interview feedback.

Interview Details:
- Role: {session_data['job_role']}
- Interview Type: {session_data['interview_type']}
- Number of Questions: {len(session_data['qa_pairs'])}
- Average Score: {avg_score:.1f}/10

Questions and Answers:
{qa_summary}

Provide comprehensive final feedback including:

1. **Overall Performance Summary** (2-3 sentences)
2. **Key Strengths** (3-4 points)
3. **Areas for Improvement** (3-4 points with specific advice)
4. **Interview Readiness Level**: Choose one:
   - Beginner: Needs significant practice
   - Intermediate: Good foundation, needs refinement
   - Job-Ready: Well-prepared for real interviews
5. **Next Steps**: Specific recommendations for improvement

Be encouraging but honest. Provide actionable advice."""
        
        return prompt
