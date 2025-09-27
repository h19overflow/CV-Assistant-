"""
Resume section extraction utilities for roadmap agent analysis.
"""

from typing import Dict, Set, Optional
import logging
from src.backend.boundary.databases.db.CRUD.resume_CRUD import get_user_resumes, get_resume

logger = logging.getLogger(__name__)

def extract_resume_sections(resume) -> Dict[str, str]:
    """
    Extract key sections for agent analysis from resume object.

    Args:
        resume: Resume object from database

    Returns:
        Dict with non-empty resume sections for analysis
    """
    # Main sections that provide value for roadmap generation
    main_sections = ['skills', 'projects', 'experience', 'education', 'summary', 'certificates']

    resume_data = {}

    for section in main_sections:
        value = getattr(resume, section, None)
        if value and str(value).strip() and str(value).strip() != "None":
            # Clean up the value
            cleaned_value = str(value).strip()

            # Skip placeholder text
            if cleaned_value.lower() not in ["no specific certificates information found.", "none"]:
                resume_data[section] = cleaned_value

    return resume_data

def get_user_resume_sections(user_id: str, resume_id: Optional[str] = None) -> Dict[str, str]:
    """
    Get resume sections for a specific user.

    Args:
        user_id: User ID to get resume for
        resume_id: Optional specific resume ID, uses latest if not provided

    Returns:
        Dict with resume sections for analysis

    Raises:
        ValueError: If no resume found for user
    """
    try:
        if resume_id:
            # Get specific resume
            resume = get_resume(resume_id)
            if not resume or resume.user_id != user_id:
                raise ValueError("Resume not found or doesn't belong to user")
        else:
            # Get latest resume for user
            resumes = get_user_resumes(user_id)
            if not resumes:
                raise ValueError("No resumes found for user")
            resume = resumes[-1]  # Get most recent

        # Extract sections
        sections = extract_resume_sections(resume)

        # Add metadata
        sections['filename'] = resume.filename
        sections['user_id'] = str(resume.user_id)

        logger.info(f"Extracted {len(sections)} sections from resume: {resume.filename}")
        return sections

    except Exception as e:
        logger.error(f"Failed to get resume sections for user {user_id}: {e}")
        raise

def get_main_section_keys() -> Set[str]:
    """
    Get the set of main section keys used for analysis.

    Returns:
        Set of section key names
    """
    return {
        'skills',
        'projects',
        'experience',
        'education',
        'summary',
        'certificates',
        'filename',
        'user_id'
    }

def format_sections_for_agent(sections: Dict[str, str]) -> str:
    """
    Format resume sections into a structured string for agent analysis.

    Args:
        sections: Dict of resume sections

    Returns:
        Formatted string for agent processing
    """
    formatted = "RESUME ANALYSIS DATA:\n\n"

    # Order sections by importance for analysis
    section_order = ['summary', 'skills', 'experience', 'projects', 'education', 'certificates']

    for section_key in section_order:
        if section_key in sections:
            formatted += f"{section_key.upper()}:\n"
            formatted += f"{sections[section_key]}\n\n"

    # Add metadata at the end
    if 'filename' in sections:
        formatted += f"SOURCE FILE: {sections['filename']}\n"

    return formatted

# HELPER FUNCTIONS

def analyze_resume_completeness(sections: Dict[str, str]) -> Dict[str, any]:
    """
    Analyze how complete a resume is based on available sections.

    Args:
        sections: Resume sections dict

    Returns:
        Analysis of resume completeness
    """
    main_sections = {'skills', 'projects', 'experience', 'education'}
    available_sections = set(sections.keys())

    # Calculate completeness
    available_main = main_sections.intersection(available_sections)
    completeness_score = len(available_main) / len(main_sections)

    # Identify missing sections
    missing_sections = main_sections - available_sections

    return {
        'completeness_score': completeness_score,
        'available_sections': list(available_main),
        'missing_sections': list(missing_sections),
        'total_sections': len(available_sections),
        'has_summary': 'summary' in sections,
        'has_certificates': 'certificates' in sections
    }


def _extract_key_indicators(sections: Dict[str, str]) -> Dict[str, any]:
    """
    Extract key indicators from resume sections for quick analysis.

    Args:
        sections: Resume sections dict

    Returns:
        Dict with key indicators and insights
    """
    indicators = {
        'has_technical_skills': False,
        'has_projects': False,
        'has_work_experience': False,
        'experience_level': 'Unknown',
        'primary_technologies': [],
        'education_level': 'Unknown'
    }

    # Analyze skills section
    if 'skills' in sections:
        skills_text = sections['skills'].lower()
        indicators['has_technical_skills'] = True

        # Extract common technologies
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'tensorflow', 'pytorch',
            'sql', 'docker', 'kubernetes', 'aws', 'azure', 'machine learning',
            'deep learning', 'data science', 'fastapi', 'flask', 'django'
        ]

        found_techs = [tech for tech in tech_keywords if tech in skills_text]
        indicators['primary_technologies'] = found_techs[:5]  # Top 5

    # Analyze projects section
    if 'projects' in sections:
        indicators['has_projects'] = True

    # Analyze experience section
    if 'experience' in sections:
        experience_text = sections['experience'].lower()
        indicators['has_work_experience'] = True

        # Determine experience level
        if any(term in experience_text for term in ['senior', 'lead', 'principal']):
            indicators['experience_level'] = 'Senior'
        elif any(term in experience_text for term in ['junior', 'entry', 'intern']):
            indicators['experience_level'] = 'Junior'
        elif any(term in experience_text for term in ['student', 'expected graduation']):
            indicators['experience_level'] = 'Student'
        else:
            indicators['experience_level'] = 'Intermediate'

    # Analyze education section
    if 'education' in sections:
        education_text = sections['education'].lower()

        if 'phd' in education_text or 'doctorate' in education_text:
            indicators['education_level'] = 'PhD'
        elif 'master' in education_text or 'msc' in education_text or 'ma ' in education_text:
            indicators['education_level'] = 'Masters'
        elif 'bachelor' in education_text or 'bsc' in education_text or 'ba ' in education_text:
            indicators['education_level'] = 'Bachelors'
        else:
            indicators['education_level'] = 'Other'

    return indicators