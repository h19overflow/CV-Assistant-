"""
Database package for Resume System.
Provides models, engine, and utilities for database operations.
"""

from .models import User, Resume, Feedback, Base
from .engine import (
    DatabaseManager,
    get_db_manager,
    get_session,
    get_session_context
)
from src.backend.boundary.databases.db.CRUD.auth_CRUD import (
    AuthCRUD,
    create_user,
    login_user,
    get_user,
    AuthError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError
)

__all__ = [
    # Models
    'User',
    'Resume',
    'Feedback',
    'Base',

    # Engine & Sessions
    'DatabaseManager',
    'get_db_manager',
    'get_session',
    'get_session_context',

    # Authentication
    'AuthCRUD',
    'create_user',
    'login_user',
    'get_user',
    'AuthError',
    'UserAlreadyExistsError',
    'UserNotFoundError',
    'InvalidCredentialsError'
]