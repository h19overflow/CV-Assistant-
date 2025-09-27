"""
Pydantic schemas for Career Chat Multi-Agent System.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request for sending a chat message"""
    session_id: str = Field(description="Chat session identifier")
    message: str = Field(description="User message content")
    include_context: bool = Field(default=True, description="Whether to include resume/roadmap context")


class ChatResponse(BaseModel):
    """Response from career chat agent"""
    session_id: str = Field(description="Chat session identifier")
    agent_response: str = Field(description="Agent's response message")
    context_used: Dict[str, Any] = Field(description="Context data that was used")
    timestamp: datetime = Field(description="Response timestamp")
    success: bool = Field(description="Whether the request succeeded")


class StartSessionRequest(BaseModel):
    """Request to start a new chat session"""
    user_id: str = Field(description="User identifier")
    resume_id: Optional[str] = Field(default=None, description="Specific resume to use for context")
    roadmap_id: Optional[str] = Field(default=None, description="Specific roadmap to reference")
    initial_context: Optional[str] = Field(default=None, description="Initial context or goal")


class StartSessionResponse(BaseModel):
    """Response when starting a new chat session"""
    session_id: str = Field(description="Generated session identifier")
    context_summary: str = Field(description="Summary of loaded context")
    initial_message: str = Field(description="Agent's initial greeting message")
    success: bool = Field(description="Whether session creation succeeded")


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(description="Message role (human, ai, system)")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(description="Message timestamp")


class ChatHistoryResponse(BaseModel):
    """Response containing chat history"""
    session_id: str = Field(description="Chat session identifier")
    messages: List[ChatMessage] = Field(description="List of messages in chronological order")
    total_messages: int = Field(description="Total number of messages")
    session_start: datetime = Field(description="When the session started")


class UserContext(BaseModel):
    """User context for career chat"""
    user_id: str = Field(description="User identifier")
    resume_sections: Dict[str, str] = Field(description="Resume sections data")
    roadmaps: List[Dict[str, Any]] = Field(description="User's career roadmaps")
    current_goal: Optional[str] = Field(description="Current career goal")


class AgentContextData(BaseModel):
    """Context data for the career chat agent"""
    user_context: UserContext = Field(description="User-specific context")
    conversation_history: List[ChatMessage] = Field(description="Recent conversation history")
    session_metadata: Dict[str, Any] = Field(description="Session metadata and settings")


class CareerAdviceResponse(BaseModel):
    """Structured response from career chat agent"""
    advice: str = Field(description="Main career advice")
    references: List[str] = Field(description="References to resume sections or roadmap steps")
    suggestions: List[str] = Field(description="Specific actionable suggestions")
    confidence: float = Field(description="Confidence in the advice (0-1)")
    follow_up_questions: List[str] = Field(description="Suggested follow-up questions")