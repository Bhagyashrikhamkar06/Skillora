"""
Profile scraper service for GitHub, LeetCode, and LinkedIn
"""
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

class ProfileScraper:
    """Scrape and analyze social coding profiles"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')  # Optional, increases rate limit
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
    
    # ============================================
    # GITHUB API INTEGRATION
    # ============================================
    
    def scrape_github_profile(self, username: str) -> Dict:
        """
        Scrape GitHub profile using official API
        Returns comprehensive GitHub statistics
        """
        cache_key = f"github_{username}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            # Get user profile
            user_url = f'https://api.github.com/users/{username}'
            user_response = requests.get(user_url, headers=headers, timeout=10)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get repositories
            repos_url = f'https://api.github.com/users/{username}/repos?per_page=100&sort=updated'
            repos_response = requests.get(repos_url, headers=headers, timeout=10)
            repos_response.raise_for_status()
            repos_data = repos_response.json()
            
            # Calculate statistics
            total_stars = sum(repo.get('stargazers_count', 0) for repo in repos_data)
            total_forks = sum(repo.get('forks_count', 0) for repo in repos_data)
            
            # Get language statistics
            languages = {}
            for repo in repos_data:
                if repo.get('language'):
                    languages[repo['language']] = languages.get(repo['language'], 0) + 1
            
            # Sort languages by frequency
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Get contribution data (last year)
            # Note: This requires GraphQL API for detailed contribution graph
            # For now, we'll use basic stats
            
            result = {
                'username': username,
                'name': user_data.get('name'),
                'bio': user_data.get('bio'),
                'avatar_url': user_data.get('avatar_url'),
                'public_repos': user_data.get('public_repos', 0),
                'followers': user_data.get('followers', 0),
                'following': user_data.get('following', 0),
                'total_stars': total_stars,
                'total_forks': total_forks,
                'top_languages': [{'language': lang, 'count': count} for lang, count in top_languages],
                'created_at': user_data.get('created_at'),
                'updated_at': user_data.get('updated_at'),
                'top_repos': [
                    {
                        'name': repo['name'],
                        'description': repo.get('description'),
                        'stars': repo.get('stargazers_count', 0),
                        'forks': repo.get('forks_count', 0),
                        'language': repo.get('language'),
                        'url': repo.get('html_url')
                    }
                    for repo in sorted(repos_data, key=lambda x: x.get('stargazers_count', 0), reverse=True)[:5]
                ],
                'scraped_at': datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping GitHub profile: {e}")
            return {'error': str(e), 'username': username}
    
    # ============================================
    # LEETCODE INTEGRATION (GraphQL)
    # ============================================
    
    def scrape_leetcode_profile(self, username: str) -> Dict:
        """
        Scrape LeetCode profile using GraphQL API
        Returns problem-solving statistics
        """
        cache_key = f"leetcode_{username}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # LeetCode GraphQL endpoint
            url = 'https://leetcode.com/graphql'
            
            # GraphQL query for user stats
            query = """
            query getUserProfile($username: String!) {
                matchedUser(username: $username) {
                    username
                    profile {
                        realName
                        aboutMe
                        userAvatar
                        reputation
                        ranking
                    }
                    submitStats {
                        acSubmissionNum {
                            difficulty
                            count
                        }
                    }
                    badges {
                        id
                        displayName
                        icon
                    }
                }
            }
            """
            
            payload = {
                'query': query,
                'variables': {'username': username}
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Referer': f'https://leetcode.com/{username}/'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data or not data.get('data', {}).get('matchedUser'):
                return {'error': 'User not found', 'username': username}
            
            user_data = data['data']['matchedUser']
            profile = user_data.get('profile', {})
            submit_stats = user_data.get('submitStats', {}).get('acSubmissionNum', [])
            
            # Parse submission statistics
            problems_solved = {
                'total': 0,
                'easy': 0,
                'medium': 0,
                'hard': 0
            }
            
            for stat in submit_stats:
                difficulty = stat.get('difficulty', '').lower()
                count = stat.get('count', 0)
                if difficulty == 'all':
                    problems_solved['total'] = count
                elif difficulty in problems_solved:
                    problems_solved[difficulty] = count
            
            result = {
                'username': username,
                'real_name': profile.get('realName'),
                'avatar': profile.get('userAvatar'),
                'reputation': profile.get('reputation', 0),
                'ranking': profile.get('ranking'),
                'problems_solved': problems_solved,
                'badges': [
                    {
                        'name': badge.get('displayName'),
                        'icon': badge.get('icon')
                    }
                    for badge in user_data.get('badges', [])
                ],
                'scraped_at': datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping LeetCode profile: {e}")
            return {'error': str(e), 'username': username}
    
    # ============================================
    # PROFILE LINK EXTRACTION
    # ============================================
    
    def extract_profile_links(self, text: str) -> Dict[str, str]:
        """
        Extract social profile links from resume text
        Returns dict with platform: username/url
        """
        links = {
            'github': None,
            'leetcode': None,
            'linkedin': None,
            'portfolio': None
        }
        
        # GitHub patterns
        github_patterns = [
            r'github\.com/([a-zA-Z0-9-]+)',
            r'@([a-zA-Z0-9-]+)\s+on\s+GitHub',
        ]
        for pattern in github_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                links['github'] = match.group(1)
                break
        
        # LeetCode patterns
        leetcode_patterns = [
            r'leetcode\.com/([a-zA-Z0-9_-]+)',
            r'@([a-zA-Z0-9_-]+)\s+on\s+LeetCode',
        ]
        for pattern in leetcode_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                links['leetcode'] = match.group(1)
                break
        
        # LinkedIn patterns
        linkedin_patterns = [
            r'linkedin\.com/in/([a-zA-Z0-9-]+)',
            r'linkedin\.com/pub/([a-zA-Z0-9-]+)',
        ]
        for pattern in linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                links['linkedin'] = f"linkedin.com/in/{match.group(1)}"
                break
        
        # Portfolio/personal website (basic URL detection)
        url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?'
        urls = re.findall(url_pattern, text)
        # Filter out common platforms
        excluded_domains = ['github.com', 'leetcode.com', 'linkedin.com', 'gmail.com', 'yahoo.com']
        for url in urls:
            if not any(domain in url for domain in excluded_domains):
                links['portfolio'] = url
                break
        
        return links
    
    # ============================================
    # CACHE MANAGEMENT
    # ============================================
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is in cache and not expired"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        if datetime.now() - cached_time > self.cache_duration:
            del self.cache[key]
            return False
        
        return True
    
    def _cache_data(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
