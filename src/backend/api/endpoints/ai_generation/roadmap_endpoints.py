"""
AI-powered career roadmap generation endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from src.backend.api.deps import get_current_user_id
from src.backend.core.multi_agent_systems.cv_analysis.road_maps.road_map_agent import (
    RoadMapAgent,
    get_user_resume_sections
)

router = APIRouter(prefix="/ai/roadmap", tags=["ai-roadmap"])
class RoadmapRequest(BaseModel):
    """Request for roadmap generation"""
    resume_id: Optional[str] = Field(default=None, description="Specific resume ID, if not provided uses latest")
    user_goal: str = Field(description="Target role or career goal")

class RoadmapStepResponse(BaseModel):
    """Individual roadmap step"""
    id: str = Field(description="Step identifier")
    label: str = Field(description="Step title")
    detail: Optional[str] = Field(description="Detailed instructions")
    timeframe: Optional[str] = Field(description="Estimated timeframe")
    milestone: bool = Field(description="Whether this is a key milestone")

class RoadmapEdgeResponse(BaseModel):
    """Connection between roadmap steps"""
    source: str = Field(description="Source step ID")
    target: str = Field(description="Target step ID")
    label: Optional[str] = Field(description="Edge label")

class RoadmapTextResponse(BaseModel):
    """Formatted text response for roadmap"""
    user_goal: str = Field(description="Target career goal")
    total_steps: int = Field(description="Total number of steps")
    milestones_count: int = Field(description="Number of key milestones")
    steps: List[RoadmapStepResponse] = Field(description="All roadmap steps")
    edges: List[RoadmapEdgeResponse] = Field(description="Step connections")
    formatted_text: str = Field(description="Human-readable roadmap text")
    success: bool = Field(description="Whether generation succeeded")

class MermaidResponse(BaseModel):
    """Mermaid diagram response"""
    user_goal: str = Field(description="Target career goal")
    mermaid_diagram: str = Field(description="Mermaid diagram content")
    diagram_type: str = Field(description="Type of diagram generated")
    success: bool = Field(description="Whether generation succeeded")
@router.post("/generate-text", response_model=RoadmapTextResponse)
async def generate_roadmap_text(
    request: RoadmapRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> RoadmapTextResponse:
    """
    Generate AI-powered career roadmap as formatted text.

    Args:
        request: Roadmap generation request
        current_user_id: Current authenticated user ID

    Returns:
        Formatted text roadmap with steps and suggestions

    Raises:
        404: If no resume found for user
        500: If generation fails
    """
    try:
        # Get user resume sections
        sections = get_user_resume_sections(current_user_id, request.resume_id)

        if not sections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found for user"
            )

        # Generate roadmap using the agent
        agent = RoadMapAgent()
        result = await agent.generate_roadmap(sections, request.user_goal, save_mermaid=False)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        roadmap_data = result["roadmap_steps"]

        # Convert to response format
        steps = [
            RoadmapStepResponse(
                id=step.id,
                label=step.label,
                detail=step.detail,
                timeframe=step.timeframe,
                milestone=step.milestone
            )
            for step in roadmap_data.steps
        ]

        edges = [
            RoadmapEdgeResponse(
                source=edge.source,
                target=edge.target,
                label=edge.label
            )
            for edge in roadmap_data.edges
        ]

        # Format as human-readable text
        formatted_text = _format_roadmap_text(roadmap_data, request.user_goal)

        return RoadmapTextResponse(
            user_goal=request.user_goal,
            total_steps=len(steps),
            milestones_count=sum(1 for step in steps if step.milestone),
            steps=steps,
            edges=edges,
            formatted_text=formatted_text,
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roadmap generation failed: {str(e)}"
        )
@router.post("/generate-mermaid", response_model=MermaidResponse)
async def generate_roadmap_mermaid(
    request: RoadmapRequest,
    diagram_type: str = "detailed",
    current_user_id: str = Depends(get_current_user_id)
) -> MermaidResponse:
    """
    Generate AI-powered career roadmap as Mermaid diagram.

    Args:
        request: Roadmap generation request
        diagram_type: Type of diagram ("detailed" or "clickable")
        current_user_id: Current authenticated user ID

    Returns:
        Mermaid diagram content

    Raises:
        404: If no resume found for user
        500: If generation fails
    """
    try:
        # Get user resume sections
        sections = get_user_resume_sections(current_user_id, request.resume_id)

        if not sections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found for user"
            )

        # Generate roadmap using the agent
        agent = RoadMapAgent()
        result = await agent.generate_roadmap(sections, request.user_goal, save_mermaid=True)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        # Get the appropriate Mermaid diagram
        mermaid_content = result.get("mermaid_diagram", "")

        if not mermaid_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate Mermaid diagram"
            )

        return MermaidResponse(
            user_goal=request.user_goal,
            mermaid_diagram=mermaid_content,
            diagram_type=diagram_type,
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mermaid generation failed: {str(e)}"
        )
# HELPER FUNCTIONS

def _format_roadmap_text(roadmap_data, user_goal: str) -> str:
    """
    Format roadmap data into human-readable text.

    Args:
        roadmap_data: RoadmapAgentResponse containing steps and edges
        user_goal: Target career goal

    Returns:
        Formatted text representation of the roadmap
    """
    text_lines = [
        f"# Career Roadmap: {user_goal}",
        "",
        f"This roadmap contains {len(roadmap_data.steps)} steps to help you achieve your goal.",
        "",
        "## Roadmap Steps",
        ""
    ]

    # Group steps by milestones and regular steps
    milestones = [step for step in roadmap_data.steps if step.milestone]
    regular_steps = [step for step in roadmap_data.steps if not step.milestone]

    # Add milestones section
    if milestones:
        text_lines.extend([
            "### 🎯 Key Milestones",
            ""
        ])
        for i, milestone in enumerate(milestones, 1):
            text_lines.append(f"**{i}. {milestone.label}**")
            if milestone.timeframe:
                text_lines.append(f"   ⏱️ Timeline: {milestone.timeframe}")
            if milestone.detail:
                text_lines.append(f"   📋 Details: {milestone.detail}")
            text_lines.append("")

    # Add regular steps section
    if regular_steps:
        text_lines.extend([
            "### 📌 Action Steps",
            ""
        ])
        for i, step in enumerate(regular_steps, 1):
            text_lines.append(f"**{i}. {step.label}**")
            if step.timeframe:
                text_lines.append(f"   ⏱️ Timeline: {step.timeframe}")
            if step.detail:
                text_lines.append(f"   📋 Details: {step.detail}")
            text_lines.append("")

    # Add connections overview
    if roadmap_data.edges:
        text_lines.extend([
            "## Step Dependencies",
            ""
        ])
        for edge in roadmap_data.edges:
            label_text = f" ({edge.label})" if edge.label else ""
            text_lines.append(f"• {edge.source} → {edge.target}{label_text}")

    return "\n".join(text_lines)