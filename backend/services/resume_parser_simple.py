"""
Simplified resume parsing service (no spaCy dependency)
"""
import os
import json
import re
from datetime import datetime
from pypdf import PdfReader
import docx


class ResumeParser:
    """Parse resumes and extract structured information"""
    
    def __init__(self):
        self.skill_taxonomy = self._load_skill_taxonomy()
    
    def _load_skill_taxonomy(self):
        """Load skill taxonomy from JSON"""
        try:
            taxonomy_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'skill_taxonomy.json')
            with open(taxonomy_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading skill taxonomy: {e}")
            return {}
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {e}")
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {e}")
    
    def extract_text(self, file_path):
        """Extract text based on file extension"""
        ext = file_path.rsplit('.', 1)[1].lower()
        
        if ext == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == 'docx':
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def extract_email(self, text):
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text):
        """Extract phone number from text"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else None
    
    def extract_skills(self, text):
        """Extract skills from text using skill taxonomy"""
        text_lower = text.lower()
        found_skills = []
        skill_categories = {}
        
        # Search for skills from taxonomy
        for category, skills in self.skill_taxonomy.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
                    skill_categories[skill] = category
        
        # Remove duplicates while preserving order
        unique_skills = list(dict.fromkeys(found_skills))
        
        return {
            'all_skills': unique_skills,
            'categorized': skill_categories
        }
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r'(Bachelor|B\.?S\.?|B\.?A\.?|B\.?Tech|B\.?E\.?)',
            r'(Master|M\.?S\.?|M\.?A\.?|M\.?Tech|MBA)',
            r'(Ph\.?D\.?|Doctorate)',
            r'(Associate|A\.?S\.?|A\.?A\.?)'
        ]
        
        # Find degrees
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract context around the degree
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                # Try to extract year
                year_match = re.search(r'(19|20)\d{2}', context)
                year = year_match.group() if year_match else None
                
                education.append({
                    'degree': match.group(),
                    'year': year,
                    'context': context.strip()
                })
        
        return education
    
    def extract_experience(self, text):
        """Extract work experience"""
        experience = []
        
        # Look for date ranges
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Look for date ranges (e.g., "2020 - 2023", "Jan 2020 - Present")
            date_pattern = r'(\d{4}|\w{3,9}\s+\d{4})\s*[-–—]\s*(\d{4}|\w{3,9}\s+\d{4}|Present|Current)'
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            
            if date_match:
                # Extract context (likely job title and company)
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 5)
                context = '\n'.join(lines[context_start:context_end])
                
                experience.append({
                    'date_range': date_match.group(),
                    'context': context.strip()
                })
        
        return experience
    
    def calculate_total_experience(self, experience_list):
        """Calculate total experience in months (simplified)"""
        total_months = 0
        
        for exp in experience_list:
            date_range = exp.get('date_range', '')
            # Extract years
            years = re.findall(r'\d{4}', date_range)
            if len(years) >= 2:
                try:
                    start_year = int(years[0])
                    end_year = int(years[1]) if years[1] != 'Present' else datetime.now().year
                    total_months += (end_year - start_year) * 12
                except:
                    pass
        
        return total_months
    
    def calculate_ats_score(self, parsed_data):
        """Calculate ATS (Applicant Tracking System) compatibility score"""
        score = 0.0
        max_score = 10.0
        
        # Check for contact information (2 points)
        if parsed_data.get('contact', {}).get('email'):
            score += 1.0
        if parsed_data.get('contact', {}).get('phone'):
            score += 1.0
        
        # Check for skills (3 points)
        skills = parsed_data.get('skills', {}).get('all_skills', [])
        if len(skills) >= 10:
            score += 3.0
        elif len(skills) >= 5:
            score += 2.0
        elif len(skills) > 0:
            score += 1.0
        
        # Check for education (2 points)
        if parsed_data.get('education'):
            score += 2.0
        
        # Check for experience (3 points)
        if parsed_data.get('experience'):
            score += 3.0
        
        return min(score, max_score)
    
    def parse_resume(self, file_path):
        """
        Main method to parse resume
        Returns structured data
        """
        # Extract text
        raw_text = self.extract_text(file_path)
        
        # Extract information
        email = self.extract_email(raw_text)
        phone = self.extract_phone(raw_text)
        skills_data = self.extract_skills(raw_text)
        education = self.extract_education(raw_text)
        experience = self.extract_experience(raw_text)
        total_experience_months = self.calculate_total_experience(experience)
        
        # Structure the data
        parsed_data = {
            'contact': {
                'email': email,
                'phone': phone
            },
            'skills': skills_data,
            'education': education,
            'experience': experience,
            'total_experience_months': total_experience_months,
            'raw_text': raw_text[:1000]  # Store first 1000 chars
        }
        
        # Calculate ATS score
        ats_score = self.calculate_ats_score(parsed_data)
        
        return parsed_data, ats_score
