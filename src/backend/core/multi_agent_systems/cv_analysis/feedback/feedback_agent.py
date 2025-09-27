"""
Resume feedback agent with CRUD integration and optional market research.
"""

import os
import logging
from typing import Optional, List
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from .feedback_schema import ResumeFeedback, FeedbackRequest, SkillAnalysis, SectionFeedback
from .feedback_prompt import FEEDBACK_PROMPT
from src.backend.boundary.databases.db.CRUD.resume_CRUD import get_user_resumes, get_resume
from src.backend.core.multi_agent_systems.tools.perplexity_search_tool import PerplexitySearchTool

from dotenv import load_dotenv
load_dotenv()

class FeedbackDeps(BaseModel):
    """Dependencies for the feedback agent"""
    user_id: str
    resume_id: Optional[str] = None
    enable_market_research: bool = False
    resume_data: str = ""
    market_data: str = ""

feedback_agent = Agent(
    model='gemini-2.0-flash',
    output_type=ResumeFeedback,
    deps_type=FeedbackDeps,
)

@feedback_agent.system_prompt
def dynamic_system_prompt(ctx: RunContext[FeedbackDeps]) -> str:
    """Create dynamic system prompt with resume and market data"""
    market_status = "Yes - Current job market trends included" if ctx.deps.enable_market_research else "No - Analysis based on general best practices"

    return FEEDBACK_PROMPT.format(
        resume_data=ctx.deps.resume_data,
        market_research_enabled=market_status,
        market_data=ctx.deps.market_data if ctx.deps.market_data else "No market research data available"
    )

class FeedbackAgent:
    """Resume feedback agent with CRUD integration and market research"""

    def __init__(self):
        """Initialize the feedback agent"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize Perplexity tool for market research
        self._perplexity_tool = PerplexitySearchTool()

    async def analyze_resume(self, request: FeedbackRequest) -> ResumeFeedback:
        """
        Analyze resume and provide feedback with optional market research.

        Args:
            request: Feedback request with user_id and options

        Returns:
            ResumeFeedback: Complete analysis and recommendations
        """
        try:
            # Get resume data from CRUD
            resume_data = self._get_resume_data(request.user_id, request.resume_id)
            if not resume_data:
                return self._create_error_feedback("No resume found for user")

            # Get market research if enabled
            market_data = ""
            if request.enable_market_research:
                market_data = await self._get_market_research(resume_data)

            # Create dependencies
            deps = FeedbackDeps(
                user_id=request.user_id,
                resume_id=request.resume_id,
                enable_market_research=request.enable_market_research,
                resume_data=resume_data,
                market_data=market_data
            )

            # Run agent analysis
            result = await feedback_agent.run(
                "Analyze this resume and provide comprehensive feedback",
                deps=deps
            )

            self.logger.info(f"Feedback generated for user {request.user_id}")
            return result.output

        except Exception as e:
            self.logger.error(f"Feedback analysis failed: {e}")
            return self._create_error_feedback(f"Analysis failed: {str(e)}")

    def _get_resume_data(self, user_id: str, resume_id: Optional[str] = None) -> Optional[str]:
        """Get resume data from database using CRUD operations"""
        try:
            if resume_id:
                # Get specific resume
                resume = get_resume(resume_id)
                if not resume or resume.user_id != user_id:
                    return None
            else:
                # Get latest resume for user
                resumes = get_user_resumes(user_id)
                if not resumes:
                    return None
                resume = resumes[-1]  # Get most recent

            # Format resume data for analysis
            resume_text = f"""
FILENAME: {resume.filename}

ORIGINAL TEXT:
{resume.original_text or 'No original text available'}

SUMMARY:
{resume.summary or 'No summary available'}

SKILLS:
{resume.skills or 'No skills listed'}

EXPERIENCE:
{resume.experience or 'No experience listed'}

PROJECTS:
{resume.projects or 'No projects listed'}

EDUCATION:
{resume.education or 'No education listed'}

CERTIFICATES:
{resume.certificates or 'No certificates listed'}
"""

            self.logger.info(f"Retrieved resume data for user {user_id}: {resume.filename}")
            return resume_text

        except Exception as e:
            self.logger.error(f"Failed to get resume data: {e}")
            return None

    async def _get_market_research(self, resume_data: str) -> str:
        """Get market research data using Perplexity"""
        try:
            # Extract skills from resume for market research
            skills = self._extract_skills_from_resume(resume_data)
            if not skills:
                return "No skills identified for market research"

            # Search for current market trends
            query = f"Current job market demand and trends for skills: {', '.join(skills[:10])}"  # Limit to top 5 skills

            search_response = self._perplexity_tool.search(query)

            market_info = f"MARKET RESEARCH for skills: {', '.join(skills[:10])}\n\n"
            for result in search_response.results[:3]:  # Top 3 results
                market_info += f"• {result.title}\n"
                if result.snippet:
                    market_info += f"  {result.snippet}\n"
                market_info += f"  Source: {result.url}\n\n"

            self.logger.info(f"Market research completed for {len(skills)} skills")
            return market_info

        except Exception as e:
            self.logger.warning(f"Market research failed: {e}")
            return "Market research unavailable"

    def _extract_skills_from_resume(self, resume_data: str) -> List[str]:
        """Extract skills from resume text"""
        try:
            # Simple extraction from SKILLS section
            skills_section = ""
            lines = resume_data.split('\n')
            in_skills_section = False

            for line in lines:
                if line.strip().upper().startswith('SKILLS:'):
                    in_skills_section = True
                    continue
                elif line.strip().upper().startswith(('EXPERIENCE:', 'PROJECTS:', 'EDUCATION:', 'CERTIFICATES:')):
                    in_skills_section = False
                elif in_skills_section and line.strip():
                    skills_section += line.strip() + " "

            # Basic parsing - split by common delimiters
            if skills_section:
                skills = []
                for delimiter in [',', ';', '•', '-', '\n']:
                    skills_section = skills_section.replace(delimiter, '|')

                raw_skills = [s.strip() for s in skills_section.split('|') if s.strip()]
                # Filter out very short or very long items
                skills = [s for s in raw_skills if 2 <= len(s) <= 30 and not s.isdigit()]
                return skills[:10]  # Limit to 10 skills

            return []

        except Exception as e:
            self.logger.warning(f"Skills extraction failed: {e}")
            return []

    def _create_error_feedback(self, error_message: str) -> ResumeFeedback:
        """Create error feedback response"""
        return ResumeFeedback(
            overall_score=0,
            summary=f"Analysis failed: {error_message}",
            skills_analysis=[],
            section_feedback=[
                SectionFeedback(
                    section_name="Error",
                    strengths=[],
                    weaknesses=[error_message],
                    suggestions=["Please try again or contact support"]
                )
            ],
            market_alignment=None,
            top_recommendations=["Unable to provide recommendations due to error"]
        )

# HELPER FUNCTIONS

async def analyze_user_resume(user_id: str, enable_market_research: bool = False) -> ResumeFeedback:
    """
    Simple helper function to analyze user's latest resume.

    Args:
        user_id: User ID to analyze resume for
        enable_market_research: Whether to include market research

    Returns:
        ResumeFeedback: Complete analysis and recommendations
    """
    agent = FeedbackAgent()
    request = FeedbackRequest(
        user_id=user_id,
        enable_market_research=enable_market_research
    )
    return await agent.analyze_resume(request)