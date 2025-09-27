"""
LangChain wrapper for converting between pydantic-ai and LangChain message formats.
"""

import uuid
import psycopg
from typing import List, Dict, Any
from datetime import datetime
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_postgres import PostgresChatMessageHistory

from src.backend.core.multi_agent_systems.career_chat.agent.career_chat_agent import CareerChatAgent
from src.backend.core.multi_agent_systems.career_chat.agent.career_chat_schema import CareerAdviceResponse


class LangChainChatWrapper:
    """Bridge between pydantic-ai agent and LangChain chat history"""

    def __init__(self, connection_string: str):
        """
        Initialize wrapper with database connection.

        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.agent = CareerChatAgent()
        self.table_name = "chat_history"

        # Create table if it doesn't exist
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create chat history table if it doesn't exist"""
        try:
            sync_connection = psycopg.connect(self.connection_string)
            PostgresChatMessageHistory.create_tables(sync_connection, self.table_name)
            sync_connection.close()
        except Exception as e:
            print(f"Warning: Could not create chat table: {e}")

    def start_session(self, user_context: Dict[str, Any]) -> str:
        """
        Start new chat session with user context.

        Args:
            user_context: User's resume and roadmap context

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        # Create chat history instance
        sync_connection = psycopg.connect(self.connection_string)
        chat_history = PostgresChatMessageHistory(
            table_name=self.table_name,
            session_id=session_id,
            sync_connection=sync_connection
        )

        # Add initial system message with context
        from src.backend.core.multi_agent_systems.career_chat.agent.career_chat_prompt import create_context_summary
        context_summary = create_context_summary(user_context)

        system_message = SystemMessage(
            content=f"User context loaded: {context_summary}"
        )
        chat_history.add_message(system_message)

        sync_connection.close()
        return session_id

    async def send_message(self, session_id: str, user_message: str, user_context: Dict[str, Any]) -> str:
        """
        Send message and get agent response.

        Args:
            session_id: Chat session ID
            user_message: User's message
            user_context: User's context data

        Returns:
            Agent's response message
        """
        # Get chat history
        sync_connection = psycopg.connect(self.connection_string)
        chat_history = PostgresChatMessageHistory(
            table_name=self.table_name,
            session_id=session_id,
            sync_connection=sync_connection
        )

        # Add user message
        human_message = HumanMessage(content=user_message)
        chat_history.add_message(human_message)

        # Get agent response
        try:
            advice_response = await self.agent.get_career_advice(user_message, user_context)

            # Format response text
            response_text = self._format_advice_response(advice_response)

            # Add agent response
            ai_message = AIMessage(content=response_text)
            chat_history.add_message(ai_message)

            sync_connection.close()
            return response_text

        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            ai_message = AIMessage(content=error_response)
            chat_history.add_message(ai_message)
            sync_connection.close()
            return error_response

    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history for session.

        Args:
            session_id: Chat session ID

        Returns:
            List of messages with metadata
        """
        sync_connection = psycopg.connect(self.connection_string)
        chat_history = PostgresChatMessageHistory(
            table_name=self.table_name,
            session_id=session_id,
            sync_connection=sync_connection
        )

        messages = []
        for msg in chat_history.messages:
            messages.append({
                'role': self._get_role_from_message(msg),
                'content': msg.content,
                'timestamp': datetime.now()  # LangChain doesn't store timestamps by default
            })

        sync_connection.close()
        return messages

    def _format_advice_response(self, advice: CareerAdviceResponse) -> str:
        """Format structured advice response as readable text"""
        parts = [advice.advice]

        if advice.suggestions:
            parts.append("\n**Suggestions:**")
            for suggestion in advice.suggestions:
                parts.append(f"• {suggestion}")

        if advice.references:
            parts.append("\n**Based on your:**")
            for ref in advice.references:
                parts.append(f"• {ref}")

        if advice.follow_up_questions:
            parts.append("\n**Questions to consider:**")
            for question in advice.follow_up_questions:
                parts.append(f"• {question}")

        return "\n".join(parts)

    def _get_role_from_message(self, message: BaseMessage) -> str:
        """Get role string from LangChain message type"""
        if isinstance(message, HumanMessage):
            return "human"
        elif isinstance(message, AIMessage):
            return "ai"
        elif isinstance(message, SystemMessage):
            return "system"
        else:
            return "unknown"