"""
Authentication CRUD operations for user management.
Simple password hashing using passlib.
"""

from typing import Optional
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.backend.boundary.databases.db.models import User
from src.backend.boundary.databases.db.engine import get_session_context


class AuthError(Exception):
    """Base exception for authentication errors"""
    pass


class UserAlreadyExistsError(AuthError):
    """Raised when trying to create a user that already exists"""
    pass


class UserNotFoundError(AuthError):
    """Raised when user is not found"""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when credentials are invalid"""
    pass


class AuthCRUD:
    """CRUD operations for user authentication"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing"""
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return pbkdf2_sha256.verify(password, hashed)

    @staticmethod
    def create_user(email: str, password: str) -> User:
        """
        Create a new user account.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            Created User object

        Raises:
            UserAlreadyExistsError: If email already exists
        """
        hashed_password = AuthCRUD.hash_password(password)

        with get_session_context() as session:
            try:
                new_user = User(
                    email=email.lower().strip(),
                    password_hash=hashed_password
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                return new_user

            except IntegrityError:
                session.rollback()
                raise UserAlreadyExistsError(f"User with email {email} already exists")

    @staticmethod
    def authenticate_user(email: str, password: str) -> User:
        """
        Authenticate user with email and password.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            User object if authentication successful

        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        with get_session_context() as session:
            user = session.query(User).filter(User.email == email.lower().strip()).first()

            if not user:
                raise InvalidCredentialsError("Invalid email or password")

            if not AuthCRUD.verify_password(password, user.password_hash):
                raise InvalidCredentialsError("Invalid email or password")

            return user

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User object or None if not found
        """
        with get_session_context() as session:
            return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email address

        Returns:
            User object or None if not found
        """
        with get_session_context() as session:
            return session.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def update_password(user_id: str, old_password: str, new_password: str) -> bool:
        """
        Update user password.

        Args:
            user_id: User UUID
            old_password: Current password
            new_password: New password

        Returns:
            True if password updated successfully

        Raises:
            UserNotFoundError: If user not found
            InvalidCredentialsError: If old password is incorrect
        """
        with get_session_context() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            if not AuthCRUD.verify_password(old_password, user.password_hash):
                raise InvalidCredentialsError("Current password is incorrect")

            user.password_hash = AuthCRUD.hash_password(new_password)
            session.commit()
            return True

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        Delete user account and all related data.

        Args:
            user_id: User UUID

        Returns:
            True if user deleted successfully

        Raises:
            UserNotFoundError: If user not found
        """
        with get_session_context() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            session.delete(user)  # Cascades to resumes, sections, entities, feedback
            session.commit()
            return True

    @staticmethod
    def list_users(limit: int = 100, offset: int = 0) -> list[User]:
        """
        List all users (admin function).

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of User objects
        """
        with get_session_context() as session:
            return session.query(User).offset(offset).limit(limit).all()


# Helper functions for easy usage
def create_user(email: str, password: str) -> User:
    """Create a new user - convenience function"""
    return AuthCRUD.create_user(email, password)


def login_user(email: str, password: str) -> User:
    """Authenticate user - convenience function"""
    return AuthCRUD.authenticate_user(email, password)


def get_user(user_id: str) -> Optional[User]:
    """Get user by ID - convenience function"""
    return AuthCRUD.get_user_by_id(user_id)