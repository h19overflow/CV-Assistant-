"""
Resume section extraction and analysis utilities for roadmap generation.
"""

import logging
from typing import Dict, Set, Optional
from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD
from .extract_resume_sections import (
    get_user_resume_sections,
    extract_resume_sections,
    get_main_section_keys,
    format_sections_for_agent,
    analyze_resume_completeness,
    _extract_key_indicators
)

logger = logging.getLogger(__name__)

def get_resume_analysis_data(user_id: str, resume_id: Optional[str] = None) -> Dict[str, any]:
    """
    Get comprehensive resume analysis data for roadmap generation.

    Args:
        user_id: User ID to analyze
        resume_id: Optional specific resume ID

    Returns:
        Dict with resume sections and analysis metadata
    """
    try:
        # Get resume sections
        sections = get_user_resume_sections(user_id, resume_id)

        # Analyze completeness
        completeness = analyze_resume_completeness(sections)

        # Format for agent processing
        formatted_data = format_sections_for_agent(sections)

        # Extract key skills and experience indicators
        analysis_summary = {
            'user_id': user_id,
            'resume_sections': sections,
            'completeness_analysis': completeness,
            'formatted_for_agent': formatted_data,
            'key_indicators': _extract_key_indicators(sections),
            'main_section_keys': list(get_main_section_keys())
        }

        logger.info(f"Resume analysis completed for user {user_id}")
        logger.info(f"Completeness score: {completeness['completeness_score']:.2f}")
        logger.info(f"Available sections: {', '.join(completeness['available_sections'])}")

        return analysis_summary

    except Exception as e:
        logger.error(f"Resume analysis failed for user {user_id}: {e}")
        return {
            'user_id': user_id,
            'error': str(e),
            'resume_sections': {},
            'completeness_analysis': {'completeness_score': 0},
            'formatted_for_agent': '',
            'key_indicators': {},
            'main_section_keys': list(get_main_section_keys())
        }

def print_resume_analysis(user_email: str):
    """
    Debug function to print comprehensive resume analysis.

    Args:
        user_email: Email of user to analyze
    """
    try:
        user = AuthCRUD.get_user_by_email(user_email)
        if not user:
            print(f"❌ User not found: {user_email}")
            return

        print(f"🔍 RESUME ANALYSIS FOR: {user_email}")
        print("=" * 60)

        # Get analysis data
        analysis = get_resume_analysis_data(str(user.id))

        if 'error' in analysis:
            print(f"❌ Error: {analysis['error']}")
            return

        # Print completeness analysis
        completeness = analysis['completeness_analysis']
        print(f"📊 COMPLETENESS ANALYSIS:")
        print(f"   Score: {completeness['completeness_score']:.2f} ({completeness['completeness_score']*100:.0f}%)")
        print(f"   Available: {', '.join(completeness['available_sections'])}")
        print(f"   Missing: {', '.join(completeness['missing_sections'])}")
        print(f"   Has Summary: {completeness['has_summary']}")
        print(f"   Has Certificates: {completeness['has_certificates']}")

        # Print key indicators
        indicators = analysis['key_indicators']
        print(f"\n🎯 KEY INDICATORS:")
        print(f"   Experience Level: {indicators['experience_level']}")
        print(f"   Education Level: {indicators['education_level']}")
        print(f"   Has Technical Skills: {indicators['has_technical_skills']}")
        print(f"   Has Projects: {indicators['has_projects']}")
        print(f"   Has Work Experience: {indicators['has_work_experience']}")
        print(f"   Primary Technologies: {', '.join(indicators['primary_technologies'])}")

        # Print sections summary
        sections = analysis['resume_sections']
        print(f"\n📋 SECTIONS SUMMARY:")
        for section, content in sections.items():
            if section not in ['user_id', 'filename']:
                content_preview = content
                print(f"   {section.title()}: {len(content)} chars - {content_preview}")

        print(f"\n💾 Source: {sections.get('filename', 'Unknown')}")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

# Test function
if __name__ == '__main__':
    user_email = 'hamzakhaledlklk@gmail.com'
    print_resume_analysis(user_email)