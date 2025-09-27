"""
Authentication endpoints for user registration, login, and JWT token management.
Handles secure user authentication with password hashing and JWT tokens.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

from src.backend.boundary.databases.db.CRUD.auth_CRUD import (
    AuthCRUD,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    login_with_jwt
)
from src.backend.api.deps import get_current_user_id, get_current_user
from src.backend.boundary.databases.db.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])

# Request/Response models
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User information response"""
    user_id: str
    email: str

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    user_id: str
    email: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister) -> UserResponse:
    """
    Register a new user account.

    Args:
        user_data: Email and password for new user

    Returns:
        User information without sensitive data

    Raises:
        400: If user already exists
        422: If email format is invalid
    """
    try:
        # Create new user with hashed password
        new_user = AuthCRUD.create_user(
            email=user_data.email,
            password=user_data.password
        )

        return UserResponse(
            user_id=str(new_user.id),
            email=new_user.email
        )

    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    """
    Login with email and password to get JWT access token.

    Args:
        form_data: OAuth2 form with username (email) and password

    Returns:
        JWT access token and user information

    Raises:
        401: If credentials are invalid
    """
    try:
        # Authenticate user and get JWT token
        # OAuth2PasswordRequestForm uses 'username' field for email
        login_result = login_with_jwt(
            email=form_data.username,  # FastAPI OAuth2 standard uses 'username'
            password=form_data.password
        )

        return TokenResponse(
            access_token=login_result["access_token"],
            token_type=login_result["token_type"],
            user_id=login_result["user_id"],
            email=login_result["email"]
        )

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Get current user information from JWT token.

    Args:
        current_user: User object from dependency injection

    Returns:
        Current user information
    """
    return UserResponse(
        user_id=str(current_user.id),
        email=current_user.email
    )

@router.post("/verify-token")
async def verify_token_endpoint(user_id: str = Depends(get_current_user_id)) -> Dict[str, Any]:
    """
    Verify if a JWT token is valid.

    Args:
        user_id: User ID extracted from valid token

    Returns:
        Token validation status and user ID
    """
    return {
        "valid": True,
        "user_id": user_id,
        "message": "Token is valid"
    }

# HELPER FUNCTIONS
# Note: For other endpoints, use the dependencies from src.backend.api.deps:
# - get_current_user_id: Get user ID from token
# - get_current_user: Get full User object from token
# - get_optional_user_id: Optional authentication (returns None if not authenticated)
# - get_optional_user: Optional User object (returns None if not authenticated)