"""
Resume section extraction and analysis utilities for roadmap generation.
"""

import logging
from typing import Dict, Set, Optional
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD
from .extract_resume_sections import (
    get_user_resume_sections,
    get_main_section_keys,
    format_sections_for_agent,
    analyze_resume_completeness, _extract_key_indicators
)
from .roadmap_to_mermaid import roadmap_to_mermaid, roadmap_to_mermaid_with_details, save_mermaid_to_file

logger = logging.getLogger(__name__)

class UserResume(BaseModel):
    """Dependencies for the roadmap agent"""
    sections: Dict[str, str]
    user_goal: str

class RoadmapStep(BaseModel):
    """A single step in the roadmap with Mermaid compatibility."""
    id: str  # Unique step/node identifier for mermaid (e.g. "A", "B", "C1")
    label: str  # Short description, will appear as node label in mermaid
    detail: Optional[str] = None  # Actionable instructions or details
    timeframe: Optional[str] = None  # e.g. "2 weeks", "1 month"
    milestone: Optional[bool] = False  # True if this is a key milestone

class RoadmapEdge(BaseModel):
    """A directed connection between two roadmap steps for mermaid graph"""
    source: str  # id of starting node
    target: str  # id of ending node
    label: Optional[str] = None  # Short label for the edge (optional, e.g. "after", "then")

class RoadmapAgentResponse(BaseModel):
    """Structured roadmap for Mermaid diagrams and modular usage."""
    steps: list[RoadmapStep] = []
    edges: list[RoadmapEdge] = []
    success: bool = False
    error: Optional[str] = None


# Create the roadmap agent
roadmap_agent = Agent(
    'gemini-2.5-pro',
    output_type=RoadmapAgentResponse,
    deps_type=UserResume
)

@roadmap_agent.system_prompt
def system_prompt(ctx: RunContext[UserResume]) -> str:
    """Create instructions for the roadmap agent"""
    return f"""You are an expert career roadmap generator.

Context to process:
{ctx.deps.sections}

User Goal: {ctx.deps.user_goal}

Generate a step-by-step, action-focused career roadmap that includes:
1. **Tangible actions** — Clearly specify practical steps the user can take immediately.
2. **Career progression steps** — Outline the sequence of roles, projects, or milestones that advance towards the target goal.
3. **Skills to develop** — List specific technical and soft skills, with suggestions on how to acquire them (e.g. courses, projects, certifications).
4. **Timeline estimates** — Assign realistic time frames to each step or stage.
5. **Key milestones** — Identify measurable checkpoints and achievements along the way.
6. **Clarity and guidance** — Make each action explicit, actionable, and easy to implement, so the user always knows exactly what to do next.

Ensure the roadmap is practical, motivating, and highly actionable, breaking down high-level objectives into clear tasks and recommendations.
"""

class RoadMapAgent:
    """Main roadmap agent for career path generation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def generate_roadmap(self, sections: Dict[str, str], user_goal: str, save_mermaid: bool = True) -> Dict[str, any]:
        """Generate career roadmap using AI agent"""
        if not sections:
            self.logger.error("Empty sections provided")
            return {"error": "No resume sections provided"}

        if not user_goal:
            self.logger.error("User goal is required")
            return {"error": "User goal is required"}

        try:
            # Create dependencies
            deps = UserResume(
                sections=sections,
                user_goal=user_goal
            )

            # Run the agent
            result = await roadmap_agent.run(
                "Generate a career roadmap based on the resume sections and user goal",
                deps=deps
            )

            roadmap_data = result.output
            print(roadmap_data)
            response = {
                "roadmap_steps": roadmap_data,
                "success": True
            }

            # Generate Mermaid diagrams if requested
            if save_mermaid and roadmap_data.steps and roadmap_data.edges:
                try:
                    # Generate detailed version with details in nodes
                    mermaid_detailed = roadmap_to_mermaid_with_details(roadmap_data.steps, roadmap_data.edges)

                    # Generate clickable version with details in click events
                    mermaid_clickable = roadmap_to_mermaid(roadmap_data.steps, roadmap_data.edges, include_details=True)

                    # Save to files with timestamp
                    import os
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                    # Save in the same directory as this module
                    current_dir = os.path.dirname(os.path.abspath(__file__))

                    # Save detailed version
                    detailed_filename = f"roadmap_detailed_{timestamp}.md"
                    detailed_filepath = os.path.join(current_dir, detailed_filename)
                    save_mermaid_to_file(mermaid_detailed, detailed_filepath)

                    # Save clickable version
                    clickable_filename = f"roadmap_clickable_{timestamp}.md"
                    clickable_filepath = os.path.join(current_dir, clickable_filename)
                    save_mermaid_to_file(mermaid_clickable, clickable_filepath)

                    response["mermaid_diagram"] = mermaid_detailed
                    response["mermaid_detailed_file"] = detailed_filepath
                    response["mermaid_clickable_file"] = clickable_filepath
                    self.logger.info(f"Mermaid diagrams saved to: {detailed_filepath} and {clickable_filepath}")

                except Exception as mermaid_error:
                    self.logger.warning(f"Failed to generate Mermaid diagram: {mermaid_error}")
                    response["mermaid_error"] = str(mermaid_error)

            return response

        except Exception as e:
            self.logger.error(f"Roadmap generation failed: {e}")
            return {"error": str(e)}

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
            'resume_sections': sections,
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
async def demo_roadmap_agent():
    """Demo the roadmap agent with real user data"""
    user_email = 'hamzakhaledlklk@gmail.com'

    print("🚀 ROADMAP AGENT DEMO")
    print("=" * 40)

    # Get user and sections
    user = AuthCRUD.get_user_by_email(user_email)
    if not user:
        print("❌ User not found")
        return

    sections = get_user_resume_sections(str(user.id))
    print(f"📋 Resume sections: {list(sections.keys())}")

    # Create agent and generate roadmap
    agent = RoadMapAgent()
    user_goal = "Become a Senior AI/ML Engineer"

    print(f"🎯 Goal: {user_goal}")
    print("\n🤖 Generating roadmap...")

    result = await agent.generate_roadmap(sections, user_goal)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Roadmap generated!")
        roadmap_steps = result['roadmap_steps']

        print(f"\n📋 ROADMAP STEPS ({len(roadmap_steps.steps)} steps):")
        for step in roadmap_steps.steps:
            milestone_indicator = "🎯" if step.milestone else "📌"
            print(f"   {milestone_indicator} {step.id}: {step.label}")
            if step.timeframe:
                print(f"      ⏱️  {step.timeframe}")

        print(f"\n🔗 ROADMAP EDGES ({len(roadmap_steps.edges)} connections):")
        for edge in roadmap_steps.edges:
            label_text = f" ({edge.label})" if edge.label else ""
            print(f"   {edge.source} → {edge.target}{label_text}")

        if "mermaid_detailed_file" in result:
            print(f"\n💾 Mermaid diagrams saved:")
            print(f"   📊 Detailed version: {result['mermaid_detailed_file']}")
            print(f"   🖱️  Clickable version: {result['mermaid_clickable_file']}")

        if "mermaid_error" in result:
            print(f"\n⚠️  Mermaid generation warning: {result['mermaid_error']}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(demo_roadmap_agent())