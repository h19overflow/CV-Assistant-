"""
CRUD operations for ChatSession model.
"""

from typing import Optional
from sqlalchemy.orm import Session

from ..models import ChatSession
from ..engine import get_session_context


class ChatSessionCRUD:
    """Simple CRUD operations for chat sessions"""

    @staticmethod
    def create_session(session_id: str, user_id: str) -> ChatSession:
        """Create a new chat session"""
        with get_session_context() as session:
            chat_session = ChatSession(
                session_id=session_id,
                user_id=user_id
            )
            session.add(chat_session)
            session.commit()
            session.refresh(chat_session)
            return chat_session

    @staticmethod
    def get_session(session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        with get_session_context() as session:
            return session.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    @staticmethod
    def verify_user_session(session_id: str, user_id: str) -> bool:
        """Verify if session belongs to user"""
        with get_session_context() as session:
            chat_session = session.query(ChatSession)\
                .filter(ChatSession.session_id == session_id, ChatSession.user_id == user_id)\
                .first()
            return chat_session is not None

    @staticmethod
    def delete_session(session_id: str, user_id: str) -> bool:
        """Delete session if it belongs to user"""
        with get_session_context() as session:
            chat_session = session.query(ChatSession)\
                .filter(ChatSession.session_id == session_id, ChatSession.user_id == user_id)\
                .first()

            if chat_session:
                session.delete(chat_session)
                session.commit()
                return True
            return False