"""
Authentication endpoints for user registration, login, and JWT token management.
Handles secure user authentication with password hashing and JWT tokens.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

from src.backend.boundary.databases.db.CRUD.auth_CRUD import (
    AuthCRUD,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    login_with_jwt,
    verify_jwt_token,
    get_user
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme for FastAPI to recognize Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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
async def get_current_user_info(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Get current user information from JWT token.

    Args:
        token: JWT access token from Authorization header

    Returns:
        Current user information

    Raises:
        401: If token is invalid or expired
        404: If user not found
    """
    try:
        # Verify token and extract user ID
        user_id = verify_jwt_token(token)

        # Get user from database
        user = get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(
            user_id=str(user.id),
            email=user.email
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.post("/verify-token")
async def verify_token_endpoint(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Verify if a JWT token is valid.

    Args:
        token: JWT access token from Authorization header

    Returns:
        Token validation status and user ID

    Raises:
        401: If token is invalid or expired
    """
    try:
        user_id = verify_jwt_token(token)

        return {
            "valid": True,
            "user_id": user_id,
            "message": "Token is valid"
        }

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

# HELPER FUNCTION
async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract and verify user ID from JWT token (use this in other endpoints).

    Args:
        token: JWT access token from Authorization header

    Returns:
        User ID string

    Raises:
        401: If token is invalid or expired
    """
    try:
        return verify_jwt_token(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )