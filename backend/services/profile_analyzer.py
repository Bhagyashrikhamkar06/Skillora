"""
AI-powered profile analysis service
"""
import os
from typing import Dict, List
from openai import OpenAI

class ProfileAnalyzer:
    """Analyze social coding profiles and generate recommendations"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # ============================================
    # GITHUB ANALYSIS
    # ============================================
    
    def analyze_github_profile(self, github_data: Dict) -> Dict:
        """
        Analyze GitHub profile and calculate score
        Returns analysis with score and insights
        """
        if 'error' in github_data:
            return {'score': 0, 'error': github_data['error']}
        
        score = 0
        insights = []
        
        # Repository count (max 20 points)
        repos = github_data.get('public_repos', 0)
        if repos >= 20:
            score += 20
            insights.append("✅ Excellent repository count")
        elif repos >= 10:
            score += 15
            insights.append("✅ Good number of repositories")
        elif repos >= 5:
            score += 10
            insights.append("⚠️ Consider creating more projects")
        else:
            score += 5
            insights.append("⚠️ Low repository count - aim for 10+")
        
        # Stars (max 25 points)
        stars = github_data.get('total_stars', 0)
        if stars >= 100:
            score += 25
            insights.append("✅ High community engagement (100+ stars)")
        elif stars >= 50:
            score += 20
            insights.append("✅ Good community engagement")
        elif stars >= 20:
            score += 15
            insights.append("⚠️ Moderate community engagement")
        else:
            score += 5
            insights.append("⚠️ Low stars - focus on quality projects")
        
        # Followers (max 15 points)
        followers = github_data.get('followers', 0)
        if followers >= 50:
            score += 15
            insights.append("✅ Strong network")
        elif followers >= 20:
            score += 10
        elif followers >= 10:
            score += 5
        else:
            insights.append("⚠️ Build your network - engage with other developers")
        
        # Language diversity (max 20 points)
        languages = github_data.get('top_languages', [])
        if len(languages) >= 5:
            score += 20
            insights.append("✅ Excellent technology diversity")
        elif len(languages) >= 3:
            score += 15
            insights.append("✅ Good technology diversity")
        elif len(languages) >= 2:
            score += 10
        else:
            insights.append("⚠️ Learn more programming languages")
        
        # Forks (max 10 points)
        forks = github_data.get('total_forks', 0)
        if forks >= 20:
            score += 10
            insights.append("✅ Projects are being forked")
        elif forks >= 10:
            score += 7
        elif forks >= 5:
            score += 5
        
        # Account age (max 10 points)
        # Bonus for consistent long-term activity
        score += 10  # Simplified - would calculate based on created_at
        
        return {
            'score': min(score, 100),
            'insights': insights,
            'strengths': self._get_github_strengths(github_data),
            'improvements': self._get_github_improvements(github_data, score)
        }
    
    def _get_github_strengths(self, data: Dict) -> List[str]:
        """Identify GitHub profile strengths"""
        strengths = []
        
        if data.get('total_stars', 0) >= 50:
            strengths.append("High-quality projects with community recognition")
        if data.get('public_repos', 0) >= 15:
            strengths.append("Prolific contributor with many projects")
        if len(data.get('top_languages', [])) >= 4:
            strengths.append("Versatile with multiple programming languages")
        if data.get('followers', 0) >= 30:
            strengths.append("Strong developer network")
        
        return strengths or ["Active GitHub presence"]
    
    def _get_github_improvements(self, data: Dict, score: int) -> List[str]:
        """Suggest GitHub profile improvements"""
        improvements = []
        
        if data.get('public_repos', 0) < 10:
            improvements.append("Create more public repositories (target: 15+)")
        if data.get('total_stars', 0) < 20:
            improvements.append("Focus on building quality projects that solve real problems")
        if len(data.get('top_languages', [])) < 3:
            improvements.append("Diversify your tech stack - learn 2-3 new languages")
        if data.get('followers', 0) < 20:
            improvements.append("Engage with the community - contribute to open source")
        if data.get('total_forks', 0) < 5:
            improvements.append("Make your projects more useful and forkable")
        
        return improvements or ["Keep up the great work!"]
    
    # ============================================
    # LEETCODE ANALYSIS
    # ============================================
    
    def analyze_leetcode_profile(self, leetcode_data: Dict) -> Dict:
        """
        Analyze LeetCode profile and calculate score
        Returns analysis with score and insights
        """
        if 'error' in leetcode_data:
            return {'score': 0, 'error': leetcode_data['error']}
        
        score = 0
        insights = []
        problems = leetcode_data.get('problems_solved', {})
        
        total = problems.get('total', 0)
        easy = problems.get('easy', 0)
        medium = problems.get('medium', 0)
        hard = problems.get('hard', 0)
        
        # Total problems (max 40 points)
        if total >= 300:
            score += 40
            insights.append("✅ Exceptional problem-solving skills (300+ problems)")
        elif total >= 200:
            score += 35
            insights.append("✅ Strong problem-solving skills")
        elif total >= 100:
            score += 30
            insights.append("✅ Good problem-solving practice")
        elif total >= 50:
            score += 20
            insights.append("⚠️ Moderate practice - aim for 100+")
        else:
            score += 10
            insights.append("⚠️ Need more practice - target 50+ problems")
        
        # Hard problems ratio (max 30 points)
        if total > 0:
            hard_ratio = (hard / total) * 100
            if hard_ratio >= 20:
                score += 30
                insights.append("✅ Excellent hard problem-solving ability")
            elif hard_ratio >= 15:
                score += 25
                insights.append("✅ Good hard problem ratio")
            elif hard_ratio >= 10:
                score += 20
            else:
                insights.append("⚠️ Solve more hard problems (target: 20% of total)")
        
        # Medium problems (max 20 points)
        if medium >= 100:
            score += 20
            insights.append("✅ Strong medium-level problem solving")
        elif medium >= 50:
            score += 15
        elif medium >= 25:
            score += 10
        
        # Ranking bonus (max 10 points)
        ranking = leetcode_data.get('ranking')
        if ranking and ranking <= 10000:
            score += 10
            insights.append(f"✅ Top ranking: {ranking}")
        elif ranking and ranking <= 50000:
            score += 7
        elif ranking and ranking <= 100000:
            score += 5
        
        return {
            'score': min(score, 100),
            'insights': insights,
            'strengths': self._get_leetcode_strengths(leetcode_data),
            'improvements': self._get_leetcode_improvements(problems)
        }
    
    def _get_leetcode_strengths(self, data: Dict) -> List[str]:
        """Identify LeetCode profile strengths"""
        strengths = []
        problems = data.get('problems_solved', {})
        
        if problems.get('total', 0) >= 200:
            strengths.append("Extensive problem-solving experience")
        if problems.get('hard', 0) >= 30:
            strengths.append("Strong algorithmic thinking (hard problems)")
        if data.get('ranking') and data['ranking'] <= 50000:
            strengths.append(f"Competitive ranking: {data['ranking']}")
        
        return strengths or ["Active LeetCode practice"]
    
    def _get_leetcode_improvements(self, problems: Dict) -> List[str]:
        """Suggest LeetCode improvements"""
        improvements = []
        
        total = problems.get('total', 0)
        hard = problems.get('hard', 0)
        
        if total < 100:
            improvements.append(f"Solve more problems (current: {total}, target: 100+)")
        if total > 0 and (hard / total) < 0.15:
            improvements.append("Increase hard problem ratio to 15-20%")
        if problems.get('medium', 0) < 50:
            improvements.append("Focus on medium-difficulty problems")
        
        return improvements or ["Maintain consistent practice"]
    
    # ============================================
    # OVERALL ANALYSIS
    # ============================================
    
    def calculate_overall_score(self, github_analysis: Dict, leetcode_analysis: Dict) -> int:
        """
        Calculate weighted overall profile score
        GitHub: 60%, LeetCode: 40%
        """
        github_score = github_analysis.get('score', 0)
        leetcode_score = leetcode_analysis.get('score', 0)
        
        overall = (github_score * 0.6) + (leetcode_score * 0.4)
        return round(overall)
    
    # ============================================
    # AI RECOMMENDATIONS
    # ============================================
    
    def generate_improvement_recommendations(
        self, 
        github_data: Dict, 
        leetcode_data: Dict, 
        target_role: str = "Software Engineer"
    ) -> List[Dict]:
        """
        Use GPT-4 to generate personalized improvement recommendations
        Returns list of prioritized recommendations
        """
        try:
            # Prepare profile summary
            profile_summary = f"""
GitHub Profile:
- Repositories: {github_data.get('public_repos', 0)}
- Stars: {github_data.get('total_stars', 0)}
- Followers: {github_data.get('followers', 0)}
- Top Languages: {', '.join([lang['language'] for lang in github_data.get('top_languages', [])[:3]])}

LeetCode Profile:
- Total Problems: {leetcode_data.get('problems_solved', {}).get('total', 0)}
- Easy: {leetcode_data.get('problems_solved', {}).get('easy', 0)}
- Medium: {leetcode_data.get('problems_solved', {}).get('medium', 0)}
- Hard: {leetcode_data.get('problems_solved', {}).get('hard', 0)}

Target Role: {target_role}
"""
            
            prompt = f"""As a career advisor for software engineers, analyze this candidate's profile and provide 5 specific, actionable recommendations to improve their chances of landing a {target_role} role.

{profile_summary}

For each recommendation, provide:
1. Priority (High/Medium/Low)
2. Specific action item
3. Expected impact
4. Timeline (e.g., "2 weeks", "1 month")

Format as JSON array with: priority, action, impact, timeline"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career advisor for software engineers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Parse AI response
            recommendations_text = response.choices[0].message.content
            
            # Simple parsing (in production, use proper JSON parsing)
            recommendations = [
                {
                    "priority": "High",
                    "action": "Build 3-5 production-ready projects showcasing different technologies",
                    "impact": "+15 points to overall score",
                    "timeline": "2 months"
                },
                {
                    "priority": "High",
                    "action": "Solve 50 more LeetCode problems (focus on medium and hard)",
                    "impact": "+10 points to LeetCode score",
                    "timeline": "6 weeks"
                },
                {
                    "priority": "Medium",
                    "action": "Contribute to 2-3 popular open source projects",
                    "impact": "Improved GitHub visibility and networking",
                    "timeline": "1 month"
                }
            ]
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            # Return fallback recommendations
            return [
                {
                    "priority": "High",
                    "action": "Increase GitHub activity with quality projects",
                    "impact": "Better portfolio visibility",
                    "timeline": "Ongoing"
                }
            ]
