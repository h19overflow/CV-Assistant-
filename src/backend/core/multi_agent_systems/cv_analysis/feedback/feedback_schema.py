"""
Resume feedback schema for CV analysis agent.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class SkillAnalysis(BaseModel):
    """Analysis of a specific skill"""
    skill_name: str = Field(description="Name of the skill")
    current_level: str = Field(description="Current proficiency level (Beginner/Intermediate/Advanced)")
    market_demand: Optional[str] = Field(default=None, description="Market demand for this skill")
    improvement_suggestions: List[str] = Field(description="Specific suggestions for improvement")

class SectionFeedback(BaseModel):
    """Feedback for a specific resume section"""
    section_name: str = Field(description="Name of the section (e.g., Skills, Experience)")
    strengths: List[str] = Field(description="What's good about this section")
    weaknesses: List[str] = Field(description="Areas that need improvement")
    suggestions: List[str] = Field(description="Specific improvement suggestions")

class ResumeFeedback(BaseModel):
    """Complete resume feedback analysis"""
    overall_score: int = Field(description="Overall resume score out of 100", ge=0, le=100)
    summary: str = Field(description="Brief summary of the resume quality")
    skills_analysis: List[SkillAnalysis] = Field(description="Detailed analysis of each skill")
    section_feedback: List[SectionFeedback] = Field(description="Feedback for each resume section")
    market_alignment: Optional[str] = Field(default=None, description="How well resume aligns with current job market")
    top_recommendations: List[str] = Field(description="Top 3-5 actionable recommendations")

class FeedbackRequest(BaseModel):
    """Request for resume feedback"""
    user_id: str = Field(description="User ID to get resumes for")
    resume_id: Optional[str] = Field(default=None, description="Specific resume ID, if not provided uses latest")
    enable_market_research: bool = Field(default=False, description="Whether to use Perplexity for market research")