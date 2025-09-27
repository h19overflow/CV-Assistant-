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
# Import CRUD modules separately to avoid circular imports
# Use direct imports in your code instead of importing from __init__

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
    'get_session_context'
]