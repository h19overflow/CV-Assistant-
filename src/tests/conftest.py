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

from src.backend.api.main import app
from src.backend.boundary.databases.db.models import Base, User, Resume
from src.backend.boundary.databases.db.engine import get_session_context
from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD, create_user, login_with_jwt

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_resume_system.db"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    # Cleanup after all tests
    os.remove("./test_resume_system.db") if os.path.exists("./test_resume_system.db") else None

@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create fresh database session for each test."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()

    # Clear all tables before each test
    session.query(Resume).delete()
    session.query(User).delete()
    session.commit()

    yield session
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