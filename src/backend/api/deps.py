"""
API Dependencies for database connections and authentication.
Manages database lifecycle and provides dependency injection for FastAPI endpoints.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging

from src.backend.boundary.databases.db.engine import DatabaseManager, get_session_context
from src.backend.boundary.databases.db.CRUD.auth_CRUD import verify_jwt_token, InvalidTokenError, get_user
from src.backend.boundary.databases.db.models import User

# Setup logging
logger = logging.getLogger(__name__)

# OAuth2 scheme for JWT token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Global database manager instance
db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global db_manager
    if db_manager is None:
        raise RuntimeError("Database manager not initialized. Call init_database() first.")
    return db_manager

def init_database():
    """Initialize the database manager and create tables."""
    global db_manager
    try:
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager()
        db_manager.create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise RuntimeError(f"Database initialization failed: {e}")

def close_database():
    """Close database connections and cleanup resources."""
    global db_manager
    if db_manager:
        try:
            logger.info("Closing database connections...")
            # Add any cleanup logic here if needed
            db_manager = None
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

@asynccontextmanager
async def lifespan_manager(app) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan manager for database initialization and cleanup.

    This manages the database lifecycle:
    1. Startup: Initialize database and create tables
    2. Shutdown: Close connections and cleanup
    """
    # Startup
    try:
        logger.info("Starting up application...")
        init_database()
        logger.info("Application startup complete")
        yield
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        close_database()
        logger.info("Application shutdown complete")

# AUTHENTICATION DEPENDENCIES

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract and verify user ID from JWT token.

    Args:
        token: JWT access token from Authorization header

    Returns:
        User ID string

    Raises:
        401: If token is invalid or expired
    """
    try:
        user_id = verify_jwt_token(token)
        return user_id
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user(user_id: str = Depends(get_current_user_id)) -> User:
    """
    Get the current authenticated user from database.

    Args:
        user_id: User ID from JWT token

    Returns:
        User object from database

    Raises:
        404: If user not found in database
    """
    user = get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# DATABASE DEPENDENCIES

def get_db_session():
    """
    Get database session context manager.

    Returns:
        Database session context manager

    Usage:
        with get_db_session() as session:
            # Use session for database operations
    """
    return get_session_context()

def get_db_manager_dependency() -> DatabaseManager:
    """
    FastAPI dependency to get database manager.

    Returns:
        DatabaseManager instance

    Raises:
        500: If database manager not initialized
    """
    try:
        return get_database_manager()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# OPTIONAL AUTHENTICATION DEPENDENCIES

async def get_optional_user_id(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    """
    Get user ID from token if provided, None if not authenticated.

    Args:
        token: Optional JWT access token

    Returns:
        User ID if token valid, None otherwise
    """
    if not token:
        return None

    try:
        return verify_jwt_token(token)
    except InvalidTokenError:
        return None

async def get_optional_user(user_id: Optional[str] = Depends(get_optional_user_id)) -> Optional[User]:
    """
    Get user from database if authenticated, None otherwise.

    Args:
        user_id: Optional user ID from token

    Returns:
        User object if authenticated, None otherwise
    """
    if not user_id:
        return None

    return get_user(user_id)