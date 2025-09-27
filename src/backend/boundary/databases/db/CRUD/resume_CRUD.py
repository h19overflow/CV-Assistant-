"""
Resume CRUD operations for CV management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.backend.boundary.databases.db import AuthCRUD
from src.backend.boundary.databases.db.models import Resume
from src.backend.boundary.databases.db.engine import get_session_context


def create_resume(user_id: str, filename: str, original_text: str = None, summary: str = None,
                 skills: str = None, experience: str = None, projects: str = None,
                 education: str = None, certificates: str = None) -> Resume:
    """Create a new resume record."""
    with get_session_context() as session:
        resume = Resume(
            user_id=user_id,
            filename=filename,
            original_text=original_text,
            summary=summary,
            skills=skills,
            experience=experience,
            projects=projects,
            education=education,
            certificates=certificates
        )
        session.add(resume)
        session.commit()
        session.refresh(resume)
        return resume


def get_resume(resume_id: str) -> Optional[Resume]:
    """Get resume by ID."""
    with get_session_context() as session:
        return session.query(Resume).filter(Resume.id == resume_id).first()


def get_user_resumes(user_id: str) -> List[Resume]:
    """Get all resumes for a user."""
    with get_session_context() as session:
        return session.query(Resume).filter(Resume.user_id == user_id).all()


def update_resume(resume_id: str, filename: str = None, original_text: str = None, summary: str = None,
                 skills: str = None, experience: str = None, projects: str = None,
                 education: str = None, certificates: str = None) -> Optional[Resume]:
    """Update resume fields."""
    with get_session_context() as session:
        resume = session.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return None

        if filename is not None:
            resume.filename = filename
        if original_text is not None:
            resume.original_text = original_text
        if summary is not None:
            resume.summary = summary
        if skills is not None:
            resume.skills = skills
        if experience is not None:
            resume.experience = experience
        if projects is not None:
            resume.projects = projects
        if education is not None:
            resume.education = education
        if certificates is not None:
            resume.certificates = certificates

        session.commit()
        session.refresh(resume)
        return resume


def delete_resume(resume_id: str) -> bool:
    """Delete a resume."""
    with get_session_context() as session:
        resume = session.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return False

        session.delete(resume)
        session.commit()
        return True


def get_resume_by_filename(user_id: str, filename: str) -> Optional[Resume]:
    """Get resume by user ID and filename."""
    with get_session_context() as session:
        return session.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.filename == filename
        ).first()


if __name__ == '__main__':
    user_email = "hamzakhaledlklk@gmail.com"
    from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD

    user = AuthCRUD.get_user_by_email(user_email)
    print(f"User: {user}")
    print("-" * 50)

    result = get_user_resumes(user_id=user.id)
    print(f"Found {len(result)} resumes for user {user.email}")
    print("-" * 50)

    for i, row in enumerate(result):
        print(f"Resume {i + 1}:")
        print(f"  ID: {row.id}")
        print(f"  Filename: {row.filename}")
        print(f"  User ID: {row.user_id}")
        print(f"  Original Text: {len(row.original_text) if row.original_text else 0} chars")
        print(f"  Summary: {len(row.summary) if row.summary else 0} chars")
        print(f"  Skills: {len(row.skills) if row.skills else 0} chars")
        print(f"  Experience: {len(row.experience) if row.experience else 0} chars")
        print(f"  Projects: {len(row.projects) if row.projects else 0} chars")
        print(f"  Education: {len(row.education) if row.education else 0} chars")
        print(f"  Certificates: {len(row.certificates) if row.certificates else 0} chars")
        print("-" * 30)