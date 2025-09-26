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

    # Relationships
    user = relationship("User", back_populates="resumes")
    sections = relationship("Section", back_populates="resume", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename={self.filename})>"


class Section(Base):
    """Resume sections table (Education, Skills, Projects, etc.)"""
    __tablename__ = 'sections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id'), nullable=False)
    section_type = Column(String(100), nullable=False)  # Education, Skills, Projects, Experience, Summary
    content = Column(Text)
    start_pos = Column(Integer)  # Character offset in original_text
    end_pos = Column(Integer)
    embedding = Column(BYTEA)  # Optional: for section-level RAG

    # Relationships
    resume = relationship("Resume", back_populates="sections")
    entities = relationship("Entity", back_populates="section", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Section(id={self.id}, type={self.section_type}, resume_id={self.resume_id})>"


class Entity(Base):
    """Extracted entities from resume sections"""
    __tablename__ = 'entities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey('sections.id'), nullable=False)
    entity_type = Column(String(100), nullable=False)  # Skill, ProjectName, Company, Degree, Certification
    value = Column(String(255), nullable=False)
    normalized = Column(String(255))  # For standardized lookups/matching

    # Relationships
    section = relationship("Section", back_populates="entities")

    def __repr__(self):
        return f"<Entity(id={self.id}, type={self.entity_type}, value={self.value})>"


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
