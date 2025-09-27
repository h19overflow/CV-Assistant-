"""
AI-powered resume feedback endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional

from src.backend.api.deps import get_current_user_id
from src.backend.core.multi_agent_systems.cv_analysis.feedback import (
    analyze_user_resume,
    ResumeFeedback,
    SkillAnalysis,
    SectionFeedback
)

router = APIRouter(prefix="/ai/feedback", tags=["ai-feedback"])

class FeedbackRequest(BaseModel):
    """Request for resume feedback"""
    resume_id: Optional[str] = Field(default=None, description="Specific resume ID, if not provided uses latest")
    enable_market_research: bool = Field(default=False, description="Whether to include market research")

class FeedbackResponse(BaseModel):
    """Response with resume feedback"""
    overall_score: int = Field(description="Overall resume score out of 100")
    summary: str = Field(description="Brief summary of the resume quality")
    skills_analysis: list[SkillAnalysis] = Field(description="Detailed analysis of each skill")
    section_feedback: list[SectionFeedback] = Field(description="Feedback for each resume section")
    market_alignment: Optional[str] = Field(description="How well resume aligns with current job market")
    top_recommendations: list[str] = Field(description="Top actionable recommendations")

@router.post("/analyze", response_model=FeedbackResponse)
async def get_resume_feedback(
    request: FeedbackRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> FeedbackResponse:
    """
    Get AI-powered feedback for user's resume.

    Args:
        request: Feedback request with options
        current_user_id: Current authenticated user ID

    Returns:
        Comprehensive resume feedback and recommendations

    Raises:
        404: If no resume found for user
        500: If analysis fails
    """
    try:
        # Run AI analysis
        feedback = await analyze_user_resume(
            user_id=current_user_id,
            enable_market_research=request.enable_market_research
        )

        # Check if analysis failed
        if feedback.overall_score == 0 and "failed" in feedback.summary.lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=feedback.summary
            )

        return FeedbackResponse(
            overall_score=feedback.overall_score,
            summary=feedback.summary,
            skills_analysis=feedback.skills_analysis,
            section_feedback=feedback.section_feedback,
            market_alignment=feedback.market_alignment,
            top_recommendations=feedback.top_recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback analysis failed: {str(e)}"
        )

@router.post("/analyze/{resume_id}", response_model=FeedbackResponse)
async def get_specific_resume_feedback(
    resume_id: str,
    enable_market_research: bool = False,
    current_user_id: str = Depends(get_current_user_id)
) -> FeedbackResponse:
    """
    Get AI-powered feedback for a specific resume.

    Args:
        resume_id: Specific resume ID to analyze
        enable_market_research: Whether to include market research
        current_user_id: Current authenticated user ID

    Returns:
        Comprehensive resume feedback and recommendations

    Raises:
        404: If resume not found or doesn't belong to user
        500: If analysis fails
    """
    try:
        # Import here to avoid circular imports
        from src.backend.core.multi_agent_systems.cv_analysis.feedback import FeedbackAgent, FeedbackRequest as AgentRequest

        agent = FeedbackAgent()
        request = AgentRequest(
            user_id=current_user_id,
            resume_id=resume_id,
            enable_market_research=enable_market_research
        )

        feedback = await agent.analyze_resume(request)

        # Check if analysis failed
        if feedback.overall_score == 0 and "failed" in feedback.summary.lower():
            if "not found" in feedback.summary.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resume not found or doesn't belong to user"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=feedback.summary
                )

        return FeedbackResponse(
            overall_score=feedback.overall_score,
            summary=feedback.summary,
            skills_analysis=feedback.skills_analysis,
            section_feedback=feedback.section_feedback,
            market_alignment=feedback.market_alignment,
            top_recommendations=feedback.top_recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback analysis failed: {str(e)}"
        )