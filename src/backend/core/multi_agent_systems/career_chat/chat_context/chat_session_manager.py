"""
Chat session manager that orchestrates all career chat components.
"""

import os
from typing import Dict, Any, Optional

from .langchain_wrapper import LangChainChatWrapper
from .chat_context_manager import ChatContextManager
from src.backend.core.multi_agent_systems.career_chat.agent.career_chat_prompt import create_initial_greeting
from src.backend.boundary.databases.db.CRUD.chat_session_CRUD import ChatSessionCRUD


class ChatSessionManager:
    """Orchestrates career chat sessions with full context integration"""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize session manager.

        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string or os.getenv('POSTGRES_CONNECTION_STRING')
        if not self.connection_string:
            raise ValueError("POSTGRES_CONNECTION_STRING environment variable is required")

        self.chat_wrapper = LangChainChatWrapper(self.connection_string)
        self.context_manager = ChatContextManager()

    def start_session(self, user_id: str, resume_id: Optional[str] = None, roadmap_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start new chat session with user context.

        Args:
            user_id: User identifier
            resume_id: Optional specific resume ID
            roadmap_id: Optional specific roadmap ID

        Returns:
            Session initialization response
        """
        try:
            # Load user context
            user_context = self.context_manager.load_user_context(user_id, resume_id, roadmap_id)

            # Start LangChain session
            session_id = self.chat_wrapper.start_session(user_context)

            # Track session ownership in database
            ChatSessionCRUD.create_session(session_id, user_id)

            # Create initial greeting
            initial_message = create_initial_greeting(user_context)

            # Get context summary
            context_summary = self.context_manager.get_context_summary(user_context)

            return {
                'session_id': session_id,
                'initial_message': initial_message,
                'context_summary': context_summary,
                'success': True
            }

        except Exception as e:
            return {
                'session_id': None,
                'initial_message': f"Sorry, I couldn't start the chat session: {str(e)}",
                'context_summary': "No context available",
                'success': False,
                'error': str(e)
            }

    async def send_message(self, session_id: str, user_message: str, user_id: str) -> Dict[str, Any]:
        """
        Send message and get agent response.

        Args:
            session_id: Chat session ID
            user_message: User's message
            user_id: User identifier for context refresh

        Returns:
            Agent response with metadata
        """
        try:
            # Verify session belongs to user
            if not ChatSessionCRUD.verify_user_session(session_id, user_id):
                raise ValueError("Session not found or access denied")

            # Refresh user context for current message
            user_context = self.context_manager.load_user_context(user_id)

            # Send message through wrapper
            agent_response = await self.chat_wrapper.send_message(session_id, user_message, user_context)

            return {
                'session_id': session_id,
                'agent_response': agent_response,
                'success': True
            }

        except Exception as e:
            return {
                'session_id': session_id,
                'agent_response': f"I apologize, but I encountered an error: {str(e)}",
                'success': False,
                'error': str(e)
            }

    def get_chat_history(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get chat history for session.

        Args:
            session_id: Chat session ID
            user_id: User identifier for ownership verification

        Returns:
            Chat history with metadata
        """
        try:
            # Verify session belongs to user
            if not ChatSessionCRUD.verify_user_session(session_id, user_id):
                raise ValueError("Session not found or access denied")

            messages = self.chat_wrapper.get_chat_history(session_id)

            return {
                'session_id': session_id,
                'messages': messages,
                'total_messages': len(messages),
                'success': True
            }

        except Exception as e:
            return {
                'session_id': session_id,
                'messages': [],
                'total_messages': 0,
                'success': False,
                'error': str(e)
            }

    def clear_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Clear/delete a chat session.

        Args:
            session_id: Chat session ID
            user_id: User identifier for ownership verification

        Returns:
            Deletion result
        """
        try:
            # Delete session from database (this also verifies ownership)
            deleted = ChatSessionCRUD.delete_session(session_id, user_id)

            if deleted:
                return {
                    'session_id': session_id,
                    'success': True,
                    'message': 'Session cleared successfully'
                }
            else:
                return {
                    'session_id': session_id,
                    'success': False,
                    'error': 'Session not found or access denied'
                }

        except Exception as e:
            return {
                'session_id': session_id,
                'success': False,
                'error': str(e)
            }