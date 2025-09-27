"""
Career Chat Multi-Agent System for Resume System.

This module provides AI-powered career counseling through chat interactions,
integrating with user resume data and generated roadmaps for personalized advice.
"""

from src.backend.core.multi_agent_systems.career_chat.agent.career_chat_agent import CareerChatAgent
from src.backend.core.multi_agent_systems.career_chat.chat_context.chat_session_manager import ChatSessionManager
from src.backend.core.multi_agent_systems.career_chat.agent.career_chat_schema import (
    ChatRequest,
    ChatResponse,
    StartSessionRequest,
    StartSessionResponse,
    ChatHistoryResponse
)

__all__ = [
    "CareerChatAgent",
    "ChatSessionManager",
    "ChatRequest",
    "ChatResponse",
    "StartSessionRequest",
    "StartSessionResponse",
    "ChatHistoryResponse"
]