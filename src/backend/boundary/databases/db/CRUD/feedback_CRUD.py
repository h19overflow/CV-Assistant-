"""
Feedback CRUD operations for CV analysis results.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.backend.boundary.databases.db.models import Feedback
from src.backend.boundary.databases.db.engine import get_session_context


def create_feedback(resume_id: str, feedback_text: str, category: str = None) -> Feedback:
    """Create new feedback for a resume."""
    with get_session_context() as session:
        feedback = Feedback(
            resume_id=resume_id,
            feedback_text=feedback_text,
            category=category
        )
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        return feedback


def get_feedback(feedback_id: str) -> Optional[Feedback]:
    """Get feedback by ID."""
    with get_session_context() as session:
        return session.query(Feedback).filter(Feedback.id == feedback_id).first()


def get_resume_feedback(resume_id: str) -> List[Feedback]:
    """Get all feedback for a resume."""
    with get_session_context() as session:
        return session.query(Feedback).filter(Feedback.resume_id == resume_id).all()


def get_feedback_by_category(resume_id: str, category: str) -> List[Feedback]:
    """Get feedback by resume and category."""
    with get_session_context() as session:
        return session.query(Feedback).filter(
            Feedback.resume_id == resume_id,
            Feedback.category == category
        ).all()


def update_feedback(feedback_id: str, feedback_text: str = None, category: str = None) -> Optional[Feedback]:
    """Update feedback."""
    with get_session_context() as session:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            return None

        if feedback_text is not None:
            feedback.feedback_text = feedback_text
        if category is not None:
            feedback.category = category

        session.commit()
        session.refresh(feedback)
        return feedback


def delete_feedback(feedback_id: str) -> bool:
    """Delete feedback."""
    with get_session_context() as session:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            return False

        session.delete(feedback)
        session.commit()
        return True


def delete_resume_feedback(resume_id: str) -> int:
    """Delete all feedback for a resume. Returns count of deleted records."""
    with get_session_context() as session:
        count = session.query(Feedback).filter(Feedback.resume_id == resume_id).delete()
        session.commit()
        return count