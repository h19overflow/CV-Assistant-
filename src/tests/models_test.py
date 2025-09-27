"""
Test-specific SQLAlchemy models that are SQLite compatible.
These replace PostgreSQL-specific types with SQLite equivalents.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User accounts table - test version"""
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

class Resume(Base):
    """Resumes table - test version"""
    __tablename__ = 'resumes'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    original_text = Column(Text)
    summary = Column(Text)
    filename = Column(String(255))

    # Pre-extracted sections for fast agent access
    skills = Column(Text)
    experience = Column(Text)
    projects = Column(Text)
    education = Column(Text)
    certificates = Column(Text)

    # Relationships
    user = relationship("User", back_populates="resumes")
    feedback = relationship("Feedback", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename={self.filename})>"

class Feedback(Base):
    """Feedback on resumes - test version"""
    __tablename__ = 'feedback'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey('resumes.id'), nullable=False)
    feedback_text = Column(Text, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback(id={self.id}, category={self.category}, resume_id={self.resume_id})>"