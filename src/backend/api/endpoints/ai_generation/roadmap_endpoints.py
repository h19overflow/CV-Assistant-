# """
# AI-powered career roadmap generation endpoints.
# """
#
# from fastapi import APIRouter, HTTPException, Depends, status, Response
# from pydantic import BaseModel, Field
# from typing import Optional
#
# from src.backend.api.deps import get_current_user_id
# from src.backend.core.multi_agent_systems.cv_analysis.road_maps import (
#     generate_user_roadmap,
#     RoadmapOutput,
#     RoadmapRequest as AgentRoadmapRequest,
#     OutputFormat,
#     RoadmapSize,
#     RoadmapAgent
# )
#
# router = APIRouter(prefix="/ai/roadmap", tags=["ai-roadmap"])
#
# class RoadmapRequest(BaseModel):
#     """Request for roadmap generation"""
#     resume_id: Optional[str] = Field(default=None, description="Specific resume ID, if not provided uses latest")
#     target_role: Optional[str] = Field(default=None, description="Target role for career progression")
#     enable_market_research: bool = Field(default=True, description="Whether to include market research")
#     output_format: OutputFormat = Field(default=OutputFormat.SVG, description="Desired output format")
#     max_stages: int = Field(default=8, description="Maximum number of roadmap stages", ge=3, le=15)
#
# class RoadmapResponse(BaseModel):
#     """Response with career roadmap"""
#     current_role: str = Field(description="User's current role")
#     target_role: str = Field(description="Target career goal")
#     total_duration: str = Field(description="Estimated total timeline")
#     roadmap_size: RoadmapSize = Field(description="Roadmap complexity category")
#     stages_count: int = Field(description="Number of stages in roadmap")
#     confidence_score: int = Field(description="Confidence in roadmap quality (0-100)")
#     generation_summary: str = Field(description="Summary of roadmap generation")
#     visualization_format: OutputFormat = Field(description="Format of visual output")
#     graphviz_source: str = Field(description="Generated visualization code")
#     market_research_included: bool = Field(description="Whether market research was included")
#
# @router.post("/generate", response_model=RoadmapResponse)
# async def generate_career_roadmap(
#     request: RoadmapRequest,
#     current_user_id: str = Depends(get_current_user_id)
# ) -> RoadmapResponse:
#     """
#     Generate AI-powered career roadmap for user's resume.
#
#     Args:
#         request: Roadmap generation request with options
#         current_user_id: Current authenticated user ID
#
#     Returns:
#         Comprehensive career roadmap with visualization
#
#     Raises:
#         404: If no resume found for user
#         500: If generation fails
#     """
#     try:
#         # Generate roadmap using the multi-agent system
#         roadmap_output = await generate_user_roadmap(
#             user_id=current_user_id,
#             target_role=request.target_role,
#             enable_market_research=request.enable_market_research,
#             output_format=request.output_format
#         )
#
#         # Check if generation failed
#         if roadmap_output.confidence_score == 0 and "error" in roadmap_output.generation_summary.lower():
#             if "not found" in roadmap_output.generation_summary.lower():
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="No resume found for user"
#                 )
#             else:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=roadmap_output.generation_summary
#                 )
#
#         # Create response
#         return RoadmapResponse(
#             current_role=roadmap_output.roadmap.metadata.current_role,
#             target_role=roadmap_output.roadmap.metadata.target_role,
#             total_duration=roadmap_output.roadmap.metadata.total_duration,
#             roadmap_size=roadmap_output.roadmap.metadata.roadmap_size,
#             stages_count=len(roadmap_output.roadmap.stages),
#             confidence_score=roadmap_output.confidence_score,
#             generation_summary=roadmap_output.generation_summary,
#             visualization_format=roadmap_output.visualization.output_format,
#             graphviz_source=roadmap_output.visualization.graphviz_source,
#             market_research_included=request.enable_market_research
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Roadmap generation failed: {str(e)}"
#         )
#
# @router.post("/generate/{resume_id}", response_model=RoadmapResponse)
# async def generate_specific_resume_roadmap(
#     resume_id: str,
#     target_role: Optional[str] = None,
#     enable_market_research: bool = True,
#     output_format: OutputFormat = OutputFormat.SVG,
#     max_stages: int = 8,
#     current_user_id: str = Depends(get_current_user_id)
# ) -> RoadmapResponse:
#     """
#     Generate AI-powered roadmap for a specific resume.
#
#     Args:
#         resume_id: Specific resume ID to analyze
#         target_role: Optional target role (will be inferred if not provided)
#         enable_market_research: Whether to include market research
#         output_format: Desired visualization format
#         max_stages: Maximum number of roadmap stages
#         current_user_id: Current authenticated user ID
#
#     Returns:
#         Comprehensive career roadmap with visualization
#
#     Raises:
#         404: If resume not found or doesn't belong to user
#         500: If generation fails
#     """
#     try:
#         agent = RoadmapAgent()
#         request = AgentRoadmapRequest(
#             user_id=current_user_id,
#             resume_id=resume_id,
#             target_role=target_role,
#             enable_market_research=enable_market_research,
#             output_format=output_format,
#             max_stages=max_stages
#         )
#
#         roadmap_output = await agent.generate_roadmap(request)
#
#         # Check if generation failed
#         if roadmap_output.confidence_score == 0 and "error" in roadmap_output.generation_summary.lower():
#             if "not found" in roadmap_output.generation_summary.lower():
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="Resume not found or doesn't belong to user"
#                 )
#             else:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=roadmap_output.generation_summary
#                 )
#
#         return RoadmapResponse(
#             current_role=roadmap_output.roadmap.metadata.current_role,
#             target_role=roadmap_output.roadmap.metadata.target_role,
#             total_duration=roadmap_output.roadmap.metadata.total_duration,
#             roadmap_size=roadmap_output.roadmap.metadata.roadmap_size,
#             stages_count=len(roadmap_output.roadmap.stages),
#             confidence_score=roadmap_output.confidence_score,
#             generation_summary=roadmap_output.generation_summary,
#             visualization_format=roadmap_output.visualization.output_format,
#             graphviz_source=roadmap_output.visualization.graphviz_source,
#             market_research_included=enable_market_research
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Roadmap generation failed: {str(e)}"
#         )
#
# @router.get("/render/{resume_id}")
# async def render_roadmap_image(
#     resume_id: str,
#     target_role: Optional[str] = None,
#     output_format: OutputFormat = OutputFormat.PNG,
#     current_user_id: str = Depends(get_current_user_id)
# ):
#     """
#     Generate and render roadmap as image/file.
#
#     Args:
#         resume_id: Resume ID to generate roadmap for
#         target_role: Optional target role
#         output_format: Output format (PNG, SVG, PDF)
#         current_user_id: Current authenticated user ID
#
#     Returns:
#         Rendered roadmap as file download
#
#     Raises:
#         404: If resume not found
#         500: If rendering fails
#     """
#     try:
#         # Generate roadmap
#         agent = RoadmapAgent()
#         request = AgentRoadmapRequest(
#             user_id=current_user_id,
#             resume_id=resume_id,
#             target_role=target_role,
#             enable_market_research=True,
#             output_format=output_format
#         )
#
#         roadmap_output = await agent.generate_roadmap(request)
#
#         if roadmap_output.confidence_score == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Could not generate roadmap for resume"
#             )
#
#         # Render to bytes (this would use graphviz library in actual implementation)
#         from src.backend.core.multi_agent_systems.cv_analysis.road_maps.template_engine import render_graphviz_to_format
#
#         rendered_bytes = render_graphviz_to_format(
#             roadmap_output.visualization.graphviz_source,
#             output_format
#         )
#
#         # Set appropriate content type and filename
#         content_types = {
#             OutputFormat.PNG: "image/png",
#             OutputFormat.SVG: "image/svg+xml",
#             OutputFormat.PDF: "application/pdf",
#             OutputFormat.DOT: "text/plain"
#         }
#
#         extensions = {
#             OutputFormat.PNG: "png",
#             OutputFormat.SVG: "svg",
#             OutputFormat.PDF: "pdf",
#             OutputFormat.DOT: "dot"
#         }
#
#         content_type = content_types.get(output_format, "application/octet-stream")
#         extension = extensions.get(output_format, "bin")
#         filename = f"career_roadmap_{current_user_id[:8]}.{extension}"
#
#         return Response(
#             content=rendered_bytes,
#             media_type=content_type,
#             headers={"Content-Disposition": f"attachment; filename={filename}"}
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Roadmap rendering failed: {str(e)}"
#         )
#
# @router.get("/formats")
# async def get_supported_formats():
#     """
#     Get list of supported output formats for roadmap visualization.
#
#     Returns:
#         List of supported formats with descriptions
#     """
#     return {
#         "formats": [
#             {
#                 "format": "svg",
#                 "description": "Scalable Vector Graphics - Best for web display",
#                 "mime_type": "image/svg+xml"
#             },
#             {
#                 "format": "png",
#                 "description": "Portable Network Graphics - Good for sharing",
#                 "mime_type": "image/png"
#             },
#             {
#                 "format": "pdf",
#                 "description": "Portable Document Format - Best for printing",
#                 "mime_type": "application/pdf"
#             },
#             {
#                 "format": "dot",
#                 "description": "Graphviz DOT source code - For customization",
#                 "mime_type": "text/plain"
#             }
#         ],
#         "recommended": "svg"
#     }