"""
Database engine and session management for Resume System.
Uses the same PostgreSQL database as the vector store.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv

from .models import Base

load_dotenv()


class DatabaseManager:
    """Manages database connections and sessions"""

    def __init__(self, connection_url: str = None):
        """
        Initialize database manager with connection URL.

        Args:
            connection_url: PostgreSQL connection string. Uses env var if not provided.
        """
        self.connection_url = connection_url or os.getenv('POSTGRES_CONNECTION_STRING')
        if not self.connection_url:
            raise ValueError("POSTGRES_CONNECTION_STRING environment variable is required")

        # Create engine with connection pooling
        self.engine = create_engine(
            self.connection_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before use
            echo=False  # Set to True for SQL debugging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
        except Exception as e:
            # If normal drop fails due to foreign keys, use CASCADE
            print(f"Normal drop failed: {e}")
            print("Attempting to drop with CASCADE...")
            from sqlalchemy import text
            with self.engine.connect() as connection:
                # Drop tables manually with CASCADE in dependency order
                connection.execute(text("DROP TABLE IF EXISTS entities CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS feedback CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS sections CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS resumes CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS users CASCADE"))
                connection.commit()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.

        Usage:
            with db_manager.get_session() as session:
                user = session.query(User).first()
                session.commit()
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_sync(self) -> Session:
        """Get a session for manual management (remember to close!)"""
        return self.SessionLocal()


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function for getting database sessions.
    Compatible with FastAPI dependency injection.

    Usage:
        from src.backend.boundary.databases.db.engine import get_session

        def create_user(session: Session = Depends(get_session)):
            # Use session here
    """
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        yield session


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        from src.backend.boundary.databases.db.engine import get_session_context

        with get_session_context() as session:
            user = User(email="test@example.com")
            session.add(user)
            session.commit()
    """
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        yield session

if __name__ == "__main__":
    # Example usage and test
    db_manager = get_db_manager()
    db_manager.drop_tables()
    db_manager.create_tables()
    print("Database tables dropped and recreated successfully.")