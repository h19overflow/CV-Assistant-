"""
Unit tests for authentication CRUD operations.
Tests password hashing, JWT token generation, and user management.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.backend.boundary.databases.db.CRUD.auth_CRUD import (
    AuthCRUD,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    login_with_jwt,
    verify_jwt_token,
    create_user,
    get_user
)

class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_creates_different_hash_each_time(self):
        """Test that hashing the same password twice creates different hashes."""
        password = "testpassword123"
        hash1 = AuthCRUD.hash_password(password)
        hash2 = AuthCRUD.hash_password(password)

        assert hash1 != hash2
        assert len(hash1) > 50  # Hashes should be reasonably long
        assert len(hash2) > 50

    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "correctpassword"
        hashed = AuthCRUD.hash_password(password)

        assert AuthCRUD.verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = AuthCRUD.hash_password(password)

        assert AuthCRUD.verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = "realpassword"
        hashed = AuthCRUD.hash_password(password)

        assert AuthCRUD.verify_password("", hashed) is False

class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token_contains_user_id(self):
        """Test that JWT token contains the user ID."""
        user_id = "test-user-123"
        token = AuthCRUD.create_access_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are quite long

        # Verify the token contains the user ID
        extracted_user_id = AuthCRUD.verify_access_token(token)
        assert extracted_user_id == user_id

    def test_verify_access_token_valid_token(self):
        """Test verifying a valid JWT token."""
        user_id = "valid-user-456"
        token = AuthCRUD.create_access_token(user_id)

        result = AuthCRUD.verify_access_token(token)
        assert result == user_id

    def test_verify_access_token_invalid_token(self):
        """Test verifying an invalid JWT token."""
        invalid_token = "invalid.jwt.token"

        with pytest.raises(InvalidTokenError):
            AuthCRUD.verify_access_token(invalid_token)

    def test_verify_access_token_malformed_token(self):
        """Test verifying a malformed JWT token."""
        malformed_token = "not-a-jwt-at-all"

        with pytest.raises(InvalidTokenError):
            AuthCRUD.verify_access_token(malformed_token)

    def test_verify_access_token_empty_token(self):
        """Test verifying an empty token."""
        with pytest.raises(InvalidTokenError):
            AuthCRUD.verify_access_token("")

    @patch('src.backend.boundary.databases.db.CRUD.auth_CRUD.JWT_EXPIRY_MINUTES', 0)
    def test_verify_access_token_expired_token(self):
        """Test verifying an expired JWT token."""
        user_id = "expired-user"

        # Create token that expires immediately
        with patch('src.backend.boundary.databases.db.CRUD.auth_CRUD.timedelta') as mock_timedelta:
            mock_timedelta.return_value = timedelta(seconds=-1)  # Already expired
            token = AuthCRUD.create_access_token(user_id)

        # Token should be expired, verification should fail
        with pytest.raises(InvalidTokenError):
            AuthCRUD.verify_access_token(token)

class TestUserCreation:
    """Test user creation functionality."""

    def test_create_user_success(self, test_user_data):
        """Test successful user creation."""
        user = create_user(test_user_data["email"], test_user_data["password"])

        assert user.email == test_user_data["email"].lower().strip()
        assert user.id is not None
        assert user.password_hash != test_user_data["password"]  # Should be hashed
        assert len(user.password_hash) > 50  # Hash should be substantial

    def test_create_user_duplicate_email(self, test_user_data):
        """Test creating user with duplicate email fails."""
        # Create first user
        create_user(test_user_data["email"], test_user_data["password"])

        # Attempt to create second user with same email
        with pytest.raises(UserAlreadyExistsError):
            create_user(test_user_data["email"], "differentpassword")

    def test_create_user_email_case_insensitive(self, test_user_data):
        """Test that email comparison is case insensitive."""
        # Create user with lowercase email
        create_user(test_user_data["email"].lower(), test_user_data["password"])

        # Attempt to create user with uppercase email
        with pytest.raises(UserAlreadyExistsError):
            create_user(test_user_data["email"].upper(), test_user_data["password"])

class TestAuthentication:
    """Test user authentication functionality."""

    def test_authenticate_user_success(self, created_test_user, test_user_data):
        """Test successful user authentication."""
        user = AuthCRUD.authenticate_user(
            test_user_data["email"],
            test_user_data["password"]
        )

        assert user.id == created_test_user.id
        assert user.email == created_test_user.email

    def test_authenticate_user_wrong_password(self, created_test_user, test_user_data):
        """Test authentication with wrong password."""
        with pytest.raises(InvalidCredentialsError):
            AuthCRUD.authenticate_user(
                test_user_data["email"],
                "wrongpassword"
            )

    def test_authenticate_user_nonexistent_email(self):
        """Test authentication with non-existent email."""
        with pytest.raises(InvalidCredentialsError):
            AuthCRUD.authenticate_user("nonexistent@example.com", "anypassword")

    def test_authenticate_user_empty_email(self):
        """Test authentication with empty email."""
        with pytest.raises(InvalidCredentialsError):
            AuthCRUD.authenticate_user("", "anypassword")

    def test_authenticate_user_empty_password(self, created_test_user, test_user_data):
        """Test authentication with empty password."""
        with pytest.raises(InvalidCredentialsError):
            AuthCRUD.authenticate_user(test_user_data["email"], "")

class TestLoginWithToken:
    """Test login functionality that returns JWT tokens."""

    def test_login_with_token_success(self, created_test_user, test_user_data):
        """Test successful login with JWT token return."""
        result = login_with_jwt(test_user_data["email"], test_user_data["password"])

        assert "access_token" in result
        assert "token_type" in result
        assert "user_id" in result
        assert "email" in result

        assert result["token_type"] == "bearer"
        assert result["user_id"] == str(created_test_user.id)
        assert result["email"] == created_test_user.email

        # Verify the token is valid
        extracted_user_id = verify_jwt_token(result["access_token"])
        assert extracted_user_id == str(created_test_user.id)

    def test_login_with_token_invalid_credentials(self):
        """Test login with invalid credentials."""
        with pytest.raises(InvalidCredentialsError):
            login_with_jwt("invalid@example.com", "wrongpassword")

class TestUserRetrieval:
    """Test user retrieval functionality."""

    def test_get_user_by_id_success(self, created_test_user):
        """Test successful user retrieval by ID."""
        user = get_user(str(created_test_user.id))

        assert user is not None
        assert user.id == created_test_user.id
        assert user.email == created_test_user.email

    def test_get_user_by_id_nonexistent(self):
        """Test user retrieval with non-existent ID."""
        user = get_user("nonexistent-id-123")
        assert user is None

    def test_get_user_by_email_success(self, created_test_user):
        """Test successful user retrieval by email."""
        user = AuthCRUD.get_user_by_email(created_test_user.email)

        assert user is not None
        assert user.id == created_test_user.id
        assert user.email == created_test_user.email

    def test_get_user_by_email_nonexistent(self):
        """Test user retrieval with non-existent email."""
        user = AuthCRUD.get_user_by_email("nonexistent@example.com")
        assert user is None

class TestConvenienceFunctions:
    """Test convenience functions for authentication."""

    def test_verify_jwt_token_convenience_function(self, test_user_token):
        """Test the convenience function for JWT verification."""
        user_id = verify_jwt_token(test_user_token["access_token"])
        assert user_id == test_user_token["user_id"]

    def test_verify_jwt_token_invalid_token(self):
        """Test convenience function with invalid token."""
        with pytest.raises(InvalidTokenError):
            verify_jwt_token("invalid-token")