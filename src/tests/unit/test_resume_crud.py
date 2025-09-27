"""
Unit tests for resume CRUD operations.
Tests resume creation, retrieval, updating, and deletion.
"""

import pytest
from typing import Optional

from src.backend.boundary.databases.db.CRUD.resume_CRUD import (
    create_resume,
    get_resume,
    get_user_resumes,
    update_resume,
    delete_resume,
    get_resume_by_filename
)
from src.backend.boundary.databases.db.models import Resume

class TestResumeCreation:
    """Test resume creation functionality."""

    def test_create_resume_minimal_data(self, created_test_user):
        """Test creating resume with minimal required data."""
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="minimal_resume.pdf"
        )

        assert resume.user_id == str(created_test_user.id)
        assert resume.filename == "minimal_resume.pdf"
        assert resume.id is not None
        assert resume.created_at is not None
        assert resume.updated_at is not None

        # Optional fields should be None
        assert resume.original_text is None
        assert resume.summary is None
        assert resume.skills is None
        assert resume.experience is None
        assert resume.projects is None
        assert resume.education is None
        assert resume.certificates is None

    def test_create_resume_full_data(self, created_test_user, test_resume_data):
        """Test creating resume with all data fields."""
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename=test_resume_data["filename"],
            original_text=test_resume_data["original_text"],
            summary=test_resume_data["summary"],
            skills=test_resume_data["skills"],
            experience=test_resume_data["experience"],
            projects=test_resume_data["projects"],
            education=test_resume_data["education"],
            certificates=test_resume_data["certificates"]
        )

        assert resume.user_id == str(created_test_user.id)
        assert resume.filename == test_resume_data["filename"]
        assert resume.original_text == test_resume_data["original_text"]
        assert resume.summary == test_resume_data["summary"]
        assert resume.skills == test_resume_data["skills"]
        assert resume.experience == test_resume_data["experience"]
        assert resume.projects == test_resume_data["projects"]
        assert resume.education == test_resume_data["education"]
        assert resume.certificates == test_resume_data["certificates"]

    def test_create_resume_empty_filename_fails(self, created_test_user):
        """Test that creating resume with empty filename fails."""
        with pytest.raises(Exception):  # Should fail at database level
            create_resume(user_id=str(created_test_user.id), filename="")

class TestResumeRetrieval:
    """Test resume retrieval functionality."""

    def test_get_resume_by_id_success(self, created_test_user, test_resume_data):
        """Test successful resume retrieval by ID."""
        # Create a resume first
        created_resume = create_resume(
            user_id=str(created_test_user.id),
            filename=test_resume_data["filename"],
            summary=test_resume_data["summary"]
        )

        # Retrieve the resume
        retrieved_resume = get_resume(str(created_resume.id))

        assert retrieved_resume is not None
        assert retrieved_resume.id == created_resume.id
        assert retrieved_resume.filename == test_resume_data["filename"]
        assert retrieved_resume.summary == test_resume_data["summary"]

    def test_get_resume_by_id_nonexistent(self):
        """Test resume retrieval with non-existent ID."""
        resume = get_resume("nonexistent-id-123")
        assert resume is None

    def test_get_user_resumes_empty(self, created_test_user):
        """Test getting resumes for user with no resumes."""
        resumes = get_user_resumes(str(created_test_user.id))
        assert resumes == []

    def test_get_user_resumes_multiple(self, created_test_user):
        """Test getting multiple resumes for a user."""
        # Create multiple resumes
        resume1 = create_resume(
            user_id=str(created_test_user.id),
            filename="resume1.pdf",
            summary="First resume"
        )
        resume2 = create_resume(
            user_id=str(created_test_user.id),
            filename="resume2.pdf",
            summary="Second resume"
        )

        # Retrieve all resumes for user
        resumes = get_user_resumes(str(created_test_user.id))

        assert len(resumes) == 2
        resume_ids = [str(r.id) for r in resumes]
        assert str(resume1.id) in resume_ids
        assert str(resume2.id) in resume_ids

    def test_get_user_resumes_different_users(self, test_user_data, test_user_2_data):
        """Test that users only see their own resumes."""
        # Create two users
        from src.backend.boundary.databases.db.CRUD.auth_CRUD import create_user
        user1 = create_user(test_user_data["email"], test_user_data["password"])
        user2 = create_user(test_user_2_data["email"], test_user_2_data["password"])

        # Create resumes for each user
        resume1 = create_resume(user_id=str(user1.id), filename="user1_resume.pdf")
        resume2 = create_resume(user_id=str(user2.id), filename="user2_resume.pdf")

        # Each user should only see their own resume
        user1_resumes = get_user_resumes(str(user1.id))
        user2_resumes = get_user_resumes(str(user2.id))

        assert len(user1_resumes) == 1
        assert len(user2_resumes) == 1
        assert user1_resumes[0].id == resume1.id
        assert user2_resumes[0].id == resume2.id

    def test_get_resume_by_filename_success(self, created_test_user):
        """Test successful resume retrieval by filename."""
        filename = "unique_resume.pdf"
        created_resume = create_resume(
            user_id=str(created_test_user.id),
            filename=filename
        )

        retrieved_resume = get_resume_by_filename(str(created_test_user.id), filename)

        assert retrieved_resume is not None
        assert retrieved_resume.id == created_resume.id
        assert retrieved_resume.filename == filename

    def test_get_resume_by_filename_nonexistent(self, created_test_user):
        """Test resume retrieval by non-existent filename."""
        resume = get_resume_by_filename(str(created_test_user.id), "nonexistent.pdf")
        assert resume is None

class TestResumeUpdate:
    """Test resume update functionality."""

    def test_update_resume_single_field(self, created_test_user):
        """Test updating a single field of a resume."""
        # Create resume
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="original.pdf",
            summary="Original summary"
        )

        # Update just the summary
        updated_resume = update_resume(
            resume_id=str(resume.id),
            summary="Updated summary"
        )

        assert updated_resume is not None
        assert updated_resume.summary == "Updated summary"
        assert updated_resume.filename == "original.pdf"  # Should remain unchanged

    def test_update_resume_multiple_fields(self, created_test_user, test_resume_data):
        """Test updating multiple fields of a resume."""
        # Create resume with minimal data
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="basic.pdf"
        )

        # Update multiple fields
        updated_resume = update_resume(
            resume_id=str(resume.id),
            filename=test_resume_data["filename"],
            summary=test_resume_data["summary"],
            skills=test_resume_data["skills"],
            experience=test_resume_data["experience"]
        )

        assert updated_resume is not None
        assert updated_resume.filename == test_resume_data["filename"]
        assert updated_resume.summary == test_resume_data["summary"]
        assert updated_resume.skills == test_resume_data["skills"]
        assert updated_resume.experience == test_resume_data["experience"]

    def test_update_resume_nonexistent(self):
        """Test updating non-existent resume."""
        updated_resume = update_resume(
            resume_id="nonexistent-id",
            summary="New summary"
        )
        assert updated_resume is None

    def test_update_resume_no_changes(self, created_test_user):
        """Test updating resume with no actual changes."""
        # Create resume
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="test.pdf",
            summary="Test summary"
        )

        # Update with None values (should not change anything)
        updated_resume = update_resume(resume_id=str(resume.id))

        assert updated_resume is not None
        assert updated_resume.filename == "test.pdf"
        assert updated_resume.summary == "Test summary"

class TestResumeDeletion:
    """Test resume deletion functionality."""

    def test_delete_resume_success(self, created_test_user):
        """Test successful resume deletion."""
        # Create resume
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="to_delete.pdf"
        )

        # Delete resume
        result = delete_resume(str(resume.id))
        assert result is True

        # Verify resume is deleted
        deleted_resume = get_resume(str(resume.id))
        assert deleted_resume is None

    def test_delete_resume_nonexistent(self):
        """Test deleting non-existent resume."""
        result = delete_resume("nonexistent-id")
        assert result is False

    def test_delete_resume_cascade_check(self, created_test_user):
        """Test that deleting resume doesn't affect user."""
        # Create resume
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="cascade_test.pdf"
        )

        # Delete resume
        delete_resume(str(resume.id))

        # User should still exist
        from src.backend.boundary.databases.db.CRUD.auth_CRUD import get_user
        user = get_user(str(created_test_user.id))
        assert user is not None

class TestResumeDataIntegrity:
    """Test data integrity and constraints."""

    def test_resume_timestamps(self, created_test_user):
        """Test that resume timestamps are set correctly."""
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="timestamp_test.pdf"
        )

        assert resume.created_at is not None
        assert resume.updated_at is not None
        assert resume.created_at <= resume.updated_at

    def test_resume_user_relationship(self, created_test_user, test_resume_data):
        """Test that resume is properly linked to user."""
        resume = create_resume(
            user_id=str(created_test_user.id),
            filename=test_resume_data["filename"]
        )

        # Resume should be in user's resumes
        user_resumes = get_user_resumes(str(created_test_user.id))
        resume_ids = [str(r.id) for r in user_resumes]
        assert str(resume.id) in resume_ids

    def test_large_text_fields(self, created_test_user):
        """Test handling of large text in resume fields."""
        large_text = "A" * 10000  # 10k characters

        resume = create_resume(
            user_id=str(created_test_user.id),
            filename="large_text.pdf",
            original_text=large_text,
            summary=large_text,
            experience=large_text
        )

        assert len(resume.original_text) == 10000
        assert len(resume.summary) == 10000
        assert len(resume.experience) == 10000