"""
Authentication CRUD operations for user management.
Simple password hashing using passlib and JWT token generation.

Overview:
1. User registers: Password hashed with Passlib and stored alongside a unique user ID
2. User logs in: Credentials verified, then a signed JWT returned containing user ID
3. Frontend: Sends JWT (as Bearer token) with each authorized request
4. Backend: Validates JWT and retrieves user ID for all CRUD operations
"""

from typing import Optional
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os

# JWT imports - install with: pip install python-jose[cryptography]
try:
    from jose import jwt, JWTError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("Warning: python-jose not installed. JWT features disabled.")

from src.backend.boundary.databases.db.models import User
from src.backend.boundary.databases.db.engine import get_session_context

# JWT Configuration - these should be environment variables in production
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 30  # How long the token lasts


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


class InvalidTokenError(AuthError):
    """Raised when JWT token is invalid or expired"""
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
    def create_access_token(user_id: str) -> str:
        """
        Create a JWT access token for a user.

        Args:
            user_id: The user's unique ID to include in the token

        Returns:
            JWT token string

        Raises:
            RuntimeError: If JWT library is not available
        """
        if not JWT_AVAILABLE:
            raise RuntimeError("JWT library not available. Install python-jose[cryptography]")

        # Calculate when the token expires
        expire_time = datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)

        # Create the payload - 'sub' (subject) is standard for user ID
        payload = {
            "sub": str(user_id),  # Subject - the user this token belongs to
            "exp": expire_time,   # Expiration time
            "iat": datetime.utcnow()  # Issued at time
        }

        # Sign and encode the token
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def verify_access_token(token: str) -> str:
        """
        Verify a JWT token and extract the user ID.

        Args:
            token: JWT token string

        Returns:
            User ID from the token

        Raises:
            InvalidTokenError: If token is invalid, expired, or malformed
        """
        if not JWT_AVAILABLE:
            raise RuntimeError("JWT library not available. Install python-jose[cryptography]")

        try:
            # Decode and verify the token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

            # Extract user ID from 'sub' claim
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Token missing user ID")

            return user_id

        except JWTError as e:
            # This catches expired, invalid signature, malformed tokens, etc.
            raise InvalidTokenError(f"Invalid token: {str(e)}")

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
    def login_with_token(email: str, password: str) -> dict:
        """
        Authenticate user and return JWT token (use this for login endpoints).

        Args:
            email: User email address
            password: Plain text password

        Returns:
            Dictionary with user info and access token

        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        # First authenticate the user
        user = AuthCRUD.authenticate_user(email, password)

        # Create JWT token for this user
        access_token = AuthCRUD.create_access_token(user.id)

        return {
            "user_id": str(user.id),
            "email": user.email,
            "access_token": access_token,
            "token_type": "bearer"  # Standard OAuth2 token type
        }

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


def login_with_jwt(email: str, password: str) -> dict:
    """Login and get JWT token - convenience function"""
    return AuthCRUD.login_with_token(email, password)


def verify_jwt_token(token: str) -> str:
    """Verify JWT token and get user ID - convenience function"""
    return AuthCRUD.verify_access_token(token)


def get_user(user_id: str) -> Optional[User]:
    """Get user by ID - convenience function"""
    return AuthCRUD.get_user_by_id(user_id)


if __name__ == '__main__':
    print("=== JWT Authentication Test ===")

    # Test JWT availability
    if JWT_AVAILABLE:
        print("✓ JWT library available")
    else:
        print("✗ JWT library NOT available - install with: pip install python-jose[cryptography]")
        exit(1)

    # Test user login and token generation
    test_email = "hamzakhaledlklk@gmail.com"
    test_password = "test123"  # Replace with actual password

    try:
        print(f"\n1. Testing login for: {test_email}")

        # Try to authenticate and get JWT token
        login_result = login_with_jwt(test_email, test_password)
        print("✓ Login successful!")
        print(f"   User ID: {login_result['user_id']}")
        print(f"   Email: {login_result['email']}")
        print(f"   Token Type: {login_result['token_type']}")
        print(f"   Access Token: {login_result['access_token'][:50]}...")  # Show first 50 chars

        # Test token verification
        print("\n2. Testing token verification...")
        extracted_user_id = verify_jwt_token(login_result['access_token'])
        print(f"✓ Token verified! Extracted User ID: {extracted_user_id}")

        # Verify the user IDs match
        if extracted_user_id == login_result['user_id']:
            print("✓ User IDs match - JWT system working correctly!")
        else:
            print("✗ User ID mismatch - something is wrong")

    except InvalidCredentialsError as e:
        print(f"✗ Login failed: {e}")
        print("   Make sure the email and password are correct")

    except InvalidTokenError as e:
        print(f"✗ Token verification failed: {e}")

    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    print("\n=== Test Complete ===")