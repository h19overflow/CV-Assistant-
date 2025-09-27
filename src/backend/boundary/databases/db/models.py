"""
SQLAlchemy models for Resume System database tables.
Connected to the same PostgreSQL database as the vector store.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, create_engine
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class User(Base):
    """User accounts table"""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Resume(Base):
    """Resumes table"""
    __tablename__ = 'resumes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    original_text = Column(Text)
    embedding = Column(BYTEA)  # For pgvector integration
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
    """Feedback on resumes"""
    __tablename__ = 'feedback'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id'), nullable=False)
    feedback_text = Column(Text, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback(id={self.id}, category={self.category}, resume_id={self.resume_id})>"


class CareerRoadmap(Base):
    """Career roadmaps generated for users"""
    __tablename__ = 'career_roadmaps'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id'), nullable=True)
    goal = Column(String(500), nullable=False)
    steps_data = Column(Text, nullable=False)  # JSON string of steps
    edges_data = Column(Text, nullable=False)  # JSON string of edges
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    resume = relationship("Resume")

    def __repr__(self):
        return f"<CareerRoadmap(id={self.id}, user_id={self.user_id}, goal={self.goal})>"


class ChatSession(Base):
    """Chat sessions linked to users"""
    __tablename__ = 'chat_sessions'

    session_id = Column(String(36), primary_key=True)  # UUID as string
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<ChatSession(session_id={self.session_id}, user_id={self.user_id})>"
