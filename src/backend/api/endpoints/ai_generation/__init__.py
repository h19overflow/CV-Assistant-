"""
AI generation endpoints for resume analysis, feedback, and roadmap generation.
"""

from .feedback_endpoints import router as feedback_router
from .roadmap_endpoints import router as roadmap_router

__all__ = ["feedback_router", "roadmap_router"]