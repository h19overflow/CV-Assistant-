"""
FastAPI endpoints for Career Chat functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional

from src.backend.api.deps import get_current_user_id
from src.backend.core.multi_agent_systems.career_chat import (
    ChatSessionManager,
    ChatRequest,
    ChatResponse,
    StartSessionRequest,
    StartSessionResponse,
    ChatHistoryResponse
)

router = APIRouter(prefix="/career-chat", tags=["career-chat"])

# Global session manager instance
_session_manager = None


def get_session_manager() -> ChatSessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = ChatSessionManager()
    return _session_manager


@router.post("/start-session", response_model=StartSessionResponse)
def start_chat_session(
    request: StartSessionRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> StartSessionResponse:
    """
    Start a new career chat session with user context.

    Args:
        request: Session start request
        current_user_id: Current authenticated user ID

    Returns:
        Session initialization response with greeting

    Raises:
        403: If user tries to access another user's data
        500: If session creation fails
    """
    # Verify user can only access their own data
    if request.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's data"
        )

    try:
        session_manager = get_session_manager()
        result = session_manager.start_session(
            user_id=request.user_id,
            resume_id=request.resume_id,
            roadmap_id=request.roadmap_id
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to start session')
            )

        return StartSessionResponse(
            session_id=result['session_id'],
            context_summary=result['context_summary'],
            initial_message=result['initial_message'],
            success=result['success']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session creation failed: {str(e)}"
        )


@router.post("/send-message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> ChatResponse:
    """
    Send a message to the career chat agent.

    Args:
        request: Chat message request
        current_user_id: Current authenticated user ID

    Returns:
        Agent response with advice

    Raises:
        500: If message processing fails
    """
    try:
        session_manager = get_session_manager()
        result = await session_manager.send_message(
            session_id=request.session_id,
            user_message=request.message,
            user_id=current_user_id
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to process message')
            )

        return ChatResponse(
            session_id=result['session_id'],
            agent_response=result['agent_response'],
            context_used={},  # Could be enhanced to show what context was used
            timestamp=None,   # Will be set by the response model
            success=result['success']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Message processing failed: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> ChatHistoryResponse:
    """
    Get chat history for a session.

    Args:
        session_id: Chat session ID
        current_user_id: Current authenticated user ID

    Returns:
        Complete chat history

    Raises:
        500: If history retrieval fails
    """
    try:
        session_manager = get_session_manager()
        result = session_manager.get_chat_history(session_id, current_user_id)

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to get chat history')
            )

        return ChatHistoryResponse(
            session_id=result['session_id'],
            messages=result['messages'],
            total_messages=result['total_messages'],
            session_start=None  # Could be enhanced to track session start time
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"History retrieval failed: {str(e)}"
        )


@router.delete("/clear/{session_id}")
def clear_chat_session(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Clear/delete a chat session.

    Args:
        session_id: Chat session ID
        current_user_id: Current authenticated user ID

    Returns:
        Deletion confirmation

    Raises:
        403: If session doesn't belong to user
        500: If deletion fails
    """
    try:
        session_manager = get_session_manager()
        result = session_manager.clear_session(session_id, current_user_id)

        if not result['success']:
            if 'access denied' in result.get('error', '').lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session not found or access denied"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get('error', 'Failed to clear session')
                )

        return {"message": result['message'], "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session deletion failed: {str(e)}"
        )