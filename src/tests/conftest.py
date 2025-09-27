"""
Test configuration and fixtures for pytest.
Sets up test database, authentication fixtures, and common test utilities.
"""

import pytest
import tempfile
import os
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from src.backend.api.main import app
from src.tests.models_test import Base, User, Resume  # Use test-compatible models
from src.backend.boundary.databases.db.engine import DatabaseManager, get_session_context
from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD, create_user, login_with_jwt
import contextlib
# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_resume_system.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database for all tests."""
    # Create test engine
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Mock the database manager to use test database
    test_db_manager = DatabaseManager()
    test_db_manager.engine = test_engine

    # Patch get_session_context to use test database
    @contextlib.contextmanager
    def mock_get_session_context():
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    with patch('src.backend.boundary.databases.db.engine.get_session_context', mock_get_session_context), \
         patch('src.backend.boundary.databases.db.CRUD.auth_CRUD.get_session_context', mock_get_session_context), \
         patch('src.backend.boundary.databases.db.CRUD.resume_CRUD.get_session_context', mock_get_session_context), \
         patch('src.backend.api.deps.get_database_manager', return_value=test_db_manager), \
         patch('src.backend.boundary.databases.db.CRUD.auth_CRUD.User', User), \
         patch('src.backend.boundary.databases.db.CRUD.resume_CRUD.Resume', Resume):
        yield test_engine

    # Cleanup after all tests
    try:
        if os.path.exists("./test_resume_system.db"):
            os.remove("./test_resume_system.db")
    except PermissionError:
        # Database still in use, cleanup will happen on next run
        pass

@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Clean database before each test."""
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()

    try:
        # Clear all tables before each test
        session.query(Resume).delete()
        session.query(User).delete()
        session.commit()
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_client():
    """Create FastAPI test client."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_user_data() -> Dict[str, str]:
    """Test user registration data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def test_user_2_data() -> Dict[str, str]:
    """Second test user registration data."""
    return {
        "email": "test2@example.com",
        "password": "testpassword456"
    }

@pytest.fixture
def created_test_user(test_user_data) -> User:
    """Create a test user in the database."""
    user = create_user(test_user_data["email"], test_user_data["password"])
    return user

@pytest.fixture
def test_user_token(test_user_data, created_test_user) -> Dict[str, Any]:
    """Login test user and get JWT token."""
    login_result = login_with_jwt(test_user_data["email"], test_user_data["password"])
    return login_result

@pytest.fixture
def auth_headers(test_user_token) -> Dict[str, str]:
    """Authorization headers with JWT token."""
    return {
        "Authorization": f"Bearer {test_user_token['access_token']}"
    }

@pytest.fixture
def test_resume_data() -> Dict[str, str]:
    """Test resume data."""
    return {
        "filename": "test_resume.pdf",
        "original_text": "John Doe\nSoftware Engineer\nExperience with Python, FastAPI, and databases.",
        "summary": "Experienced software engineer with 5 years in backend development.",
        "skills": "Python, FastAPI, PostgreSQL, Docker, Git",
        "experience": "5 years at TechCorp as Senior Developer",
        "projects": "Built microservices architecture, developed REST APIs",
        "education": "BS Computer Science, University of Technology",
        "certificates": "AWS Certified Developer, Python Institute PCAP"
    }

# HELPER FUNCTIONS
def create_test_user_direct(email: str = "direct@example.com", password: str = "directpass123") -> User:
    """Create a test user directly (use in tests that need specific users)."""
    return create_user(email, password)

def get_test_auth_token(email: str, password: str) -> str:
    """Get JWT token for test user."""
    result = login_with_jwt(email, password)
    return result["access_token"]

def make_auth_request(client: TestClient, method: str, url: str, token: str, **kwargs):
    """Make authenticated request to API."""
    headers = {"Authorization": f"Bearer {token}"}
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))

    return getattr(client, method.lower())(url, headers=headers, **kwargs)