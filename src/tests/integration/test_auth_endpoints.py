"""
Integration tests for authentication API endpoints.
Tests the complete authentication flow including registration, login, and protected routes.
"""

import pytest
from fastapi.testclient import TestClient

from src.backend.api.main import app

class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_user_success(self, test_client: TestClient, test_user_data):
        """Test successful user registration."""
        response = test_client.post("/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == test_user_data["email"]
        assert "password" not in data  # Password should not be returned

    def test_register_user_duplicate_email(self, test_client: TestClient, test_user_data):
        """Test registration with duplicate email fails."""
        # Register first user
        response1 = test_client.post("/auth/register", json=test_user_data)
        assert response1.status_code == 201

        # Attempt to register second user with same email
        response2 = test_client.post("/auth/register", json=test_user_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()

    def test_register_user_invalid_email(self, test_client: TestClient):
        """Test registration with invalid email format."""
        invalid_data = {
            "email": "not-an-email",
            "password": "validpassword123"
        }
        response = test_client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_register_user_missing_fields(self, test_client: TestClient):
        """Test registration with missing required fields."""
        # Missing password
        response1 = test_client.post("/auth/register", json={"email": "test@example.com"})
        assert response1.status_code == 422

        # Missing email
        response2 = test_client.post("/auth/register", json={"password": "password123"})
        assert response2.status_code == 422

        # Empty request
        response3 = test_client.post("/auth/register", json={})
        assert response3.status_code == 422

class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, test_client: TestClient, created_test_user, test_user_data):
        """Test successful user login."""
        # Use OAuth2 form data format
        form_data = {
            "username": test_user_data["email"],  # OAuth2 uses 'username' field
            "password": test_user_data["password"]
        }
        response = test_client.post("/auth/login", data=form_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user_id" in data
        assert "email" in data

        assert data["token_type"] == "bearer"
        assert data["email"] == test_user_data["email"]
        assert len(data["access_token"]) > 50  # JWT tokens are long

    def test_login_invalid_credentials(self, test_client: TestClient, created_test_user):
        """Test login with invalid credentials."""
        form_data = {
            "username": "invalid@example.com",
            "password": "wrongpassword"
        }
        response = test_client.post("/auth/login", data=form_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_wrong_password(self, test_client: TestClient, created_test_user, test_user_data):
        """Test login with correct email but wrong password."""
        form_data = {
            "username": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = test_client.post("/auth/login", data=form_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, test_client: TestClient):
        """Test login with non-existent user."""
        form_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
        response = test_client.post("/auth/login", data=form_data)

        assert response.status_code == 401

    def test_login_missing_fields(self, test_client: TestClient):
        """Test login with missing fields."""
        # Missing password
        response1 = test_client.post("/auth/login", data={"username": "test@example.com"})
        assert response1.status_code == 422

        # Missing username
        response2 = test_client.post("/auth/login", data={"password": "password123"})
        assert response2.status_code == 422

class TestProtectedEndpoints:
    """Test protected endpoints that require authentication."""

    def test_get_current_user_success(self, test_client: TestClient, auth_headers, created_test_user):
        """Test getting current user info with valid token."""
        response = test_client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert data["user_id"] == str(created_test_user.id)
        assert data["email"] == created_test_user.email

    def test_get_current_user_no_token(self, test_client: TestClient):
        """Test getting current user info without token."""
        response = test_client.get("/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, test_client: TestClient):
        """Test getting current user info with invalid token."""
        headers = {"Authorization": "Bearer invalid-token-123"}
        response = test_client.get("/auth/me", headers=headers)
        assert response.status_code == 401

    def test_get_current_user_malformed_auth_header(self, test_client: TestClient):
        """Test getting current user info with malformed auth header."""
        # Missing "Bearer " prefix
        headers = {"Authorization": "invalid-token-123"}
        response = test_client.get("/auth/me", headers=headers)
        assert response.status_code == 401

    def test_verify_token_success(self, test_client: TestClient, auth_headers, test_user_token):
        """Test token verification with valid token."""
        response = test_client.post("/auth/verify-token", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["user_id"] == test_user_token["user_id"]
        assert "message" in data

    def test_verify_token_invalid(self, test_client: TestClient):
        """Test token verification with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = test_client.post("/auth/verify-token", headers=headers)
        assert response.status_code == 401

class TestCompleteAuthFlow:
    """Test complete authentication workflow."""

    def test_complete_registration_login_flow(self, test_client: TestClient):
        """Test complete flow: register -> login -> access protected route."""
        user_data = {
            "email": "flowtest@example.com",
            "password": "flowpassword123"
        }

        # Step 1: Register user
        register_response = test_client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        user_info = register_response.json()

        # Step 2: Login to get token
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        login_response = test_client.post("/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_info = login_response.json()

        # Step 3: Use token to access protected route
        headers = {"Authorization": f"Bearer {token_info['access_token']}"}
        me_response = test_client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        me_info = me_response.json()

        # Verify consistency across all responses
        assert user_info["user_id"] == token_info["user_id"] == me_info["user_id"]
        assert user_info["email"] == token_info["email"] == me_info["email"]

    def test_token_consistency_across_endpoints(self, test_client: TestClient, auth_headers, test_user_token):
        """Test that the same token works across different protected endpoints."""
        # Test /auth/me
        me_response = test_client.get("/auth/me", headers=auth_headers)
        assert me_response.status_code == 200

        # Test /auth/verify-token
        verify_response = test_client.post("/auth/verify-token", headers=auth_headers)
        assert verify_response.status_code == 200

        # Both should return the same user_id
        me_data = me_response.json()
        verify_data = verify_response.json()
        assert me_data["user_id"] == verify_data["user_id"] == test_user_token["user_id"]

class TestAuthenticationErrors:
    """Test various authentication error scenarios."""

    def test_multiple_failed_login_attempts(self, test_client: TestClient, created_test_user, test_user_data):
        """Test multiple failed login attempts."""
        wrong_data = {
            "username": test_user_data["email"],
            "password": "wrongpassword"
        }

        # Multiple failed attempts should all return 401
        for _ in range(3):
            response = test_client.post("/auth/login", data=wrong_data)
            assert response.status_code == 401

        # Correct login should still work
        correct_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = test_client.post("/auth/login", data=correct_data)
        assert response.status_code == 200

    def test_case_insensitive_email_login(self, test_client: TestClient, created_test_user, test_user_data):
        """Test that login is case insensitive for email."""
        # Login with uppercase email
        form_data = {
            "username": test_user_data["email"].upper(),
            "password": test_user_data["password"]
        }
        response = test_client.post("/auth/login", data=form_data)
        assert response.status_code == 200

    def test_empty_authorization_header(self, test_client: TestClient):
        """Test request with empty authorization header."""
        headers = {"Authorization": ""}
        response = test_client.get("/auth/me", headers=headers)
        assert response.status_code == 401