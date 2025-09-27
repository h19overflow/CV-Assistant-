"""
AI generation endpoints for resume analysis and feedback.
"""

from .feedback_endpoints import router as feedback_router

__all__ = ["feedback_router"]